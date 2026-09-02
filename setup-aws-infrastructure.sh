#!/bin/bash

# AWS Infrastructure Setup Script for HomeChefs AI
# This script creates the necessary AWS resources using AWS CLI

set -e

# Use Windows AWS CLI (aws.exe) from WSL when no Linux 'aws' is available
if ! command -v aws &> /dev/null && command -v aws.exe &> /dev/null; then
    aws() {
        aws.exe "$@" | tr -d '\r'
    }
fi

# Configuration
REGION="ap-south-1"
PROJECT_NAME="homechefs-ai"
EC2_INSTANCE_TYPE="t3.micro"
RDS_INSTANCE_TYPE="db.t3.micro"
DOMAIN_NAME="homechefhub.in"

echo "🏗️ Setting up AWS infrastructure for HomeChefs AI..."

# Check if AWS CLI is installed and configured
if ! command -v aws &> /dev/null && ! command -v aws.exe &> /dev/null; then
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
    --vpc-id vpc-05876b94b5dd325c5 \
    --cidr-block 10.0.1.0/24 \
    --availability-zone ${REGION}a \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-public-1}]" \
    --query Subnet.SubnetId \
    --output text)

PUBLIC_SUBNET_2_ID=$(aws ec2 create-subnet \
    --vpc-id vpc-05876b94b5dd325c5 \
    --cidr-block 10.0.2.0/24 \
    --availability-zone ${REGION}b \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-public-2}]" \
    --query Subnet.SubnetId \
    --output text)

PRIVATE_SUBNET_1_ID=$(aws ec2 create-subnet \
    --vpc-id vpc-05876b94b5dd325c5 \
    --cidr-block 10.0.3.0/24 \
    --availability-zone ${REGION}a \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-private-1}]" \
    --query Subnet.SubnetId \
    --output text)

PRIVATE_SUBNET_2_ID=$(aws ec2 create-subnet \
    --vpc-id vpc-05876b94b5dd325c5 \
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

aws ec2 attach-internet-gateway --vpc-id vpc-05876b94b5dd325c5 --internet-gateway-id igw-0f24cd99b351b8ce5
echo "✅ Internet Gateway created: $IGW_ID"

# Create Route Tables
echo "🛣️ Creating Route Tables..."
PUBLIC_RT_ID=$(aws ec2 create-route-table \
    --vpc-id vpc-05876b94b5dd325c5 \
    --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=$PROJECT_NAME-public-rt}]" \
    --query RouteTable.RouteTableId \
    --output text)

aws ec2 create-route \
    --route-table-id rtb-0fad549af2cef1b3b \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id igw-0f24cd99b351b8ce5

# Associate public subnets with public route table
aws ec2 associate-route-table --route-table-id rtb-0fad549af2cef1b3b --subnet-id subnet-061754e95366132d2
aws ec2 associate-route-table --route-table-id rtb-0fad549af2cef1b3b --subnet-id subnet-0d0fee8129a3b9047

echo "✅ Route Tables created and associated"

# Create Security Groups
echo "🔒 Creating Security Groups..."

# Web Server Security Group
WEB_SG_ID=$(aws ec2 create-security-group \
    --group-name $PROJECT_NAME-web-sg \
    --description "Security group for web servers" \
    --vpc-id vpc-05876b94b5dd325c5 \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=$PROJECT_NAME-web-sg}]" \
    --query GroupId \
    --output text)

# Allow SSH, HTTP, HTTPS
aws ec2 authorize-security-group-ingress \
    --group-id sg-0a64d7b70fb024f6a \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id sg-0a64d7b70fb024f6a \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id sg-0a64d7b70fb024f6a \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Database Security Group
DB_SG_ID=$(aws ec2 create-security-group \
    --group-name $PROJECT_NAME-db-sg \
    --description "Security group for database" \
    --vpc-id vpc-05876b94b5dd325c5 \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=$PROJECT_NAME-db-sg}]" \
    --query GroupId \
    --output text)

# Allow database access from web servers
aws ec2 authorize-security-group-ingress \
    --group-id sg-030d4a9e22eea7a2c \
    --protocol tcp \
    --port 5432 \
    --source-group sg-0a64d7b70fb024f6a

echo "✅ Security Groups created:"
echo "   Web SG: sg-0a64d7b70fb024f6a"
echo "   DB SG: sg-030d4a9e22eea7a2c"

# Create RDS Subnet Group
echo "🗄️ Creating RDS Subnet Group..."
aws rds create-db-subnet-group \
    --db-subnet-group-name $PROJECT_NAME-db-subnet-group \
    --db-subnet-group-description "Subnet group for RDS database" \
    --subnet-ids subnet-0fe9c31a5a8af90f0  subnet-0c30df7b19fd0666d


#TODO
# Create RDS Database
echo "🗄️ Creating RDS PostgreSQL database..."
DB_INSTANCE_ID=$(aws rds create-db-instance \
    --db-instance-identifier $PROJECT_NAME-db \
    --db-instance-class $RDS_INSTANCE_TYPE \
    --engine postgres \
    --master-username homechefs \
    --master-user-password $(openssl rand -base64 16) \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids sg-030d4a9e22eea7a2c \
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

# Get RDS endpoint #TODO
RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier homechefs-ai-db \
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
    --output text > ./.ssh/$KEY_NAME.pem

chmod 400 ~/.ssh/$KEY_NAME.pem
echo "✅ Key pair created: $KEY_NAME (saved to ~/.ssh/$KEY_NAME.pem)"

# Create EC2 Instance #TODO
echo "🖥️ Creating EC2 instance..."
EC2_INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0ac7b260cf76d8865 \
    --instance-type $EC2_INSTANCE_TYPE \
    --key-name  $KEY_NAME \
    --security-group-ids sg-0a64d7b70fb024f6a \
    --subnet-id subnet-061754e95366132d2 \
    --associate-public-ip-address \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$PROJECT_NAME-web-server}]" \
    --query Instances[0].InstanceId \
    --output text)

echo "✅ EC2 instance creation initiated: $EC2_INSTANCE_ID"
echo "⏳ Waiting for instance to become available..."

aws ec2 wait instance-running --instance-ids i-0e5e6a714d6bb642f

# Get EC2 Public IP
EC2_PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids i-0067c8b9368ec93ff \
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
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": "'$DOMAIN_NAME'",
                        "Type": "A",
                        "TTL": 300,
                        "ResourceRecords": [
                            {
                                "Value": "'13.204.86.218'"
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

VPC ID: vpc-05876b94b5dd325c5
Public Subnets: subnet-061754e95366132d2, subnet-0d0fee8129a3b9047
Private Subnets: subnet-0fe9c31a5a8af90f0, subnet-0c30df7b19fd0666d
Internet Gateway: igw-0f24cd99b351b8ce5
Route Table: rtb-0fad549af2cef1b3b

Security Groups:
- Web SG: sg-0a64d7b70fb024f6a
- DB SG: sg-030d4a9e22eea7a2c

Database:
- RDS Instance: homechefs-ai-db
- RDS Endpoint: homechefs-ai-db.chcsuci223od.ap-south-1.rds.amazonaws.com
- Username: homechefs

Storage:
- S3 Bucket: http://homechefs-ai-media-1787548385.s3.amazonaws.com/

Compute:
- EC2 Instance: i-0e5e6a714d6bb642f
- EC2 Public IP: 13.233.163.151
- Key Pair: homechefs-ai-keypair

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
