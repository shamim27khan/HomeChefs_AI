#!/bin/bash

# AWS Infrastructure Setup Script for HomeChefs AI
# This script creates the necessary AWS resources using AWS CLI

set -e

# Configuration
REGION="ap-south-1"
PROJECT_NAME="homechefs-ai"
EC2_INSTANCE_TYPE="t3.micro"
RDS_INSTANCE_TYPE="db.t3.micro"
DOMAIN_NAME="homechefhub.in"

echo "🏗️ Setting up AWS infrastructure for HomeChefs AI..."

# Check if AWS CLI is installed and configured
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials are not configured. Please run 'aws configure' first."
    exit 1
fi

echo "📋 Using AWS Region: $REGION"
echo "📋 Project Name: $PROJECT_NAME"
echo "📋 EC2 Instance Type: $EC2_INSTANCE_TYPE"
echo "📋 RDS Instance Type: $RDS_INSTANCE_TYPE"

# Create VPC
echo "🌐 Creating VPC..."
VPC_ID=$(aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=$PROJECT_NAME-vpc}]" \
    --query Vpc.VpcId \
    --output text)

echo "✅ VPC created: $VPC_ID"

# Create Subnets
echo "🔗 Creating subnets..."
PUBLIC_SUBNET_1_ID=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone ${REGION}a \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-public-1}]" \
    --query Subnet.SubnetId \
    --output text)

PUBLIC_SUBNET_2_ID=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone ${REGION}b \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-public-2}]" \
    --query Subnet.SubnetId \
    --output text)

PRIVATE_SUBNET_1_ID=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.3.0/24 \
    --availability-zone ${REGION}a \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-private-1}]" \
    --query Subnet.SubnetId \
    --output text)

PRIVATE_SUBNET_2_ID=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.4.0/24 \
    --availability-zone ${REGION}b \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-private-2}]" \
    --query Subnet.SubnetId \
    --output text)

echo "✅ Subnets created:"
echo "   Public 1: $PUBLIC_SUBNET_1_ID"
echo "   Public 2: $PUBLIC_SUBNET_2_ID"
echo "   Private 1: $PRIVATE_SUBNET_1_ID"
echo "   Private 2: $PRIVATE_SUBNET_2_ID"

# Create Internet Gateway
echo "🌐 Creating Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway \
    --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=$PROJECT_NAME-igw}]" \
    --query InternetGateway.InternetGatewayId \
    --output text)

aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
echo "✅ Internet Gateway created: $IGW_ID"

# Create Route Tables
echo "🛣️ Creating Route Tables..."
PUBLIC_RT_ID=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=$PROJECT_NAME-public-rt}]" \
    --query RouteTable.RouteTableId \
    --output text)

aws ec2 create-route \
    --route-table-id $PUBLIC_RT_ID \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID

# Associate public subnets with public route table
aws ec2 associate-route-table --route-table-id $PUBLIC_RT_ID --subnet-id $PUBLIC_SUBNET_1_ID
aws ec2 associate-route-table --route-table-id $PUBLIC_RT_ID --subnet-id $PUBLIC_SUBNET_2_ID

echo "✅ Route Tables created and associated"

# Create Security Groups
echo "🔒 Creating Security Groups..."

# Web Server Security Group
WEB_SG_ID=$(aws ec2 create-security-group \
    --group-name $PROJECT_NAME-web-sg \
    --description "Security group for web servers" \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=$PROJECT_NAME-web-sg}]" \
    --query GroupId \
    --output text)

# Allow SSH, HTTP, HTTPS
aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Database Security Group
DB_SG_ID=$(aws ec2 create-security-group \
    --group-name $PROJECT_NAME-db-sg \
    --description "Security group for database" \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=$PROJECT_NAME-db-sg}]" \
    --query GroupId \
    --output text)

# Allow database access from web servers
aws ec2 authorize-security-group-ingress \
    --group-id $DB_SG_ID \
    --protocol tcp \
    --port 5432 \
    --source-group $WEB_SG_ID

echo "✅ Security Groups created:"
echo "   Web SG: $WEB_SG_ID"
echo "   DB SG: $DB_SG_ID"

# Create RDS Subnet Group
echo "🗄️ Creating RDS Subnet Group..."
aws rds create-db-subnet-group \
    --db-subnet-group-name $PROJECT_NAME-db-subnet-group \
    --db-subnet-group-description "Subnet group for RDS database" \
    --subnet-ids $PRIVATE_SUBNET_1_ID $PRIVATE_SUBNET_2_ID

# Create RDS Database
echo "🗄️ Creating RDS PostgreSQL database..."
DB_INSTANCE_ID=$(aws rds create-db-instance \
    --db-instance-identifier $PROJECT_NAME-db \
    --db-instance-class $RDS_INSTANCE_TYPE \
    --engine postgres \
    --engine-version 14.9 \
    --master-username homechefs \
    --master-user-password $(openssl rand -base64 16) \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids $DB_SG_ID \
    --db-subnet-group-name $PROJECT_NAME-db-subnet-group \
    --backup-retention-period 7 \
    --multi-az \
    --storage-encrypted \
    --tags Key=Name,Value=$PROJECT_NAME-database \
    --query DBInstance.DBInstanceIdentifier \
    --output text)

echo "✅ RDS Database creation initiated: $DB_INSTANCE_ID"
echo "⏳ Waiting for database to become available..."

aws rds wait db-instance-available --db-instance-identifier $DB_INSTANCE_ID

# Get RDS endpoint
RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE_ID \
    --query DBInstances[0].Endpoint.Address \
    --output text)

echo "✅ RDS Database available at: $RDS_ENDPOINT"

# Create S3 Bucket
echo "📦 Creating S3 bucket for media files..."
S3_BUCKET_NAME="$PROJECT_NAME-media-$(date +%s)"
aws s3api create-bucket \
    --bucket $S3_BUCKET_NAME \
    --region $REGION \
    --create-bucket-configuration LocationConstraint=$REGION

# Configure S3 bucket for public static website hosting
aws s3api put-bucket-cors \
    --bucket $S3_BUCKET_NAME \
    --cors-configuration '{
        "CORSRules": [
            {
                "AllowedHeaders": ["*"],
                "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
                "AllowedOrigins": ["https://homechefhub.in", "https://www.homechefhub.in"],
                "ExposeHeaders": ["ETag"]
            }
        ]
    }'

echo "✅ S3 bucket created: $S3_BUCKET_NAME"

# Create EC2 Key Pair
echo "🔑 Creating EC2 Key Pair..."
KEY_NAME="$PROJECT_NAME-keypair"
aws ec2 create-key-pair \
    --key-name $KEY_NAME \
    --query 'KeyMaterial' \
    --output text > ~/.ssh/$KEY_NAME.pem

chmod 400 ~/.ssh/$KEY_NAME.pem
echo "✅ Key pair created: $KEY_NAME (saved to ~/.ssh/$KEY_NAME.pem)"

# Create EC2 Instance
echo "🖥️ Creating EC2 instance..."
EC2_INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type $EC2_INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $WEB_SG_ID \
    --subnet-id $PUBLIC_SUBNET_1_ID \
    --associate-public-ip-address \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$PROJECT_NAME-web-server}]" \
    --query Instances[0].InstanceId \
    --output text)

echo "✅ EC2 instance creation initiated: $EC2_INSTANCE_ID"
echo "⏳ Waiting for instance to become available..."

aws ec2 wait instance-running --instance-ids $EC2_INSTANCE_ID

# Get EC2 Public IP
EC2_PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $EC2_INSTANCE_ID \
    --query Reservations[0].Instances[0].PublicIpAddress \
    --output text)

echo "✅ EC2 instance available at: $EC2_PUBLIC_IP"

# Create Route 53 Hosted Zone (if domain is managed by Route 53)
echo "🌐 Setting up Route 53..."
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones \
    --query "HostedZones[?Name==\`$DOMAIN_NAME.\`].Id" \
    --output text)

if [ -n "$HOSTED_ZONE_ID" ]; then
    echo "✅ Found existing hosted zone: $HOSTED_ZONE_ID"
    
    # Create A record for the domain
    aws route53 change-resource-record-sets \
        --hosted-zone-id $HOSTED_ZONE_ID \
        --change-batch '{
            "Changes": [
                {
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": "'$DOMAIN_NAME'",
                        "Type": "A",
                        "TTL": 300,
                        "ResourceRecords": [
                            {
                                "Value": "'$EC2_PUBLIC_IP'"
                            }
                        ]
                    }
                }
            ]
        }'
    
    echo "✅ DNS record created for $DOMAIN_NAME -> $EC2_PUBLIC_IP"
else
    echo "⚠️  Domain $DOMAIN_NAME not found in Route 53. Please configure DNS manually."
fi

# Save infrastructure details
cat > infrastructure-details.txt << EOF
AWS Infrastructure Details for HomeChefs AI
==========================================

VPC ID: $VPC_ID
Public Subnets: $PUBLIC_SUBNET_1_ID, $PUBLIC_SUBNET_2_ID
Private Subnets: $PRIVATE_SUBNET_1_ID, $PRIVATE_SUBNET_2_ID
Internet Gateway: $IGW_ID
Route Table: $PUBLIC_RT_ID

Security Groups:
- Web SG: $WEB_SG_ID
- DB SG: $DB_SG_ID

Database:
- RDS Instance: $DB_INSTANCE_ID
- RDS Endpoint: $RDS_ENDPOINT
- Username: homechefs

Storage:
- S3 Bucket: $S3_BUCKET_NAME

Compute:
- EC2 Instance: $EC2_INSTANCE_ID
- EC2 Public IP: $EC2_PUBLIC_IP
- Key Pair: $KEY_NAME

Next Steps:
1. Update deploy-aws.sh with EC2_PUBLIC_IP=$EC2_PUBLIC_IP
2. Update .env.production with RDS_ENDPOINT=$RDS_ENDPOINT
3. Update .env.production with AWS_STORAGE_BUCKET_NAME=$S3_BUCKET_NAME
4. Run deploy-aws.sh to deploy the application
EOF

echo "✅ AWS infrastructure setup completed!"
echo "📋 Details saved to infrastructure-details.txt"
echo ""
echo "🔧 Next steps:"
echo "1. Update deployment scripts with the infrastructure details"
echo "2. Configure environment variables"
echo "3. Deploy the application"
echo "4. Set up SSL certificate"
echo "5. Configure monitoring and logging"
