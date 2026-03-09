// Modal Functions for Login/Register

function showLoginModal() {
    const modalHtml = `
        <div class="modal fade" id="authModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0">
                        <h5 class="modal-title">Welcome Back!</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <!-- Login Form -->
                        <div id="loginForm">
                            <div class="text-center mb-4">
                                <h4>Login to Your Account</h4>
                                <p class="text-muted">Access your orders and favorites</p>
                            </div>
                            
                            <form id="loginFormElement">
                                <div class="mb-3">
                                    <label class="form-label">Username or Email</label>
                                    <div class="input-group">
                                        <span class="input-group-text">
                                            <i class="fas fa-user"></i>
                                        </span>
                                        <input type="text" class="form-control" id="loginUsername" 
                                               placeholder="Enter your username or email" required>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Password</label>
                                    <div class="input-group">
                                        <span class="input-group-text">
                                            <i class="fas fa-lock"></i>
                                        </span>
                                        <input type="password" class="form-control" id="loginPassword" 
                                               placeholder="Enter your password" required>
                                    </div>
                                </div>
                                
                                <div class="mb-3 form-check">
                                    <input type="checkbox" class="form-check-input" id="rememberMe">
                                    <label class="form-check-label" for="rememberMe">
                                        Remember me
                                    </label>
                                </div>
                                
                                <button type="submit" class="btn btn-primary w-100">
                                    <i class="fas fa-sign-in-alt me-2"></i>Login
                                </button>
                                
                                <div class="text-center mt-3">
                                    <a href="#" class="text-muted" onclick="showForgotPassword()">Forgot Password?</a>
                                </div>
                                
                                <div class="text-center mt-3">
                                    <span class="text-muted">Don't have an account? </span>
                                    <a href="#" class="text-primary" onclick="switchToRegister()">Sign Up</a>
                                </div>
                            </form>
                        </div>
                        
                        <!-- Register Form (Initially Hidden) -->
                        <div id="registerForm" style="display: none;">
                            <div class="text-center mb-4">
                                <h4>Create New Account</h4>
                                <p class="text-muted">Join our community of food lovers</p>
                            </div>
                            
                            <form id="registerFormElement">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">First Name</label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-user"></i>
                                            </span>
                                            <input type="text" class="form-control" id="firstName" 
                                                   placeholder="First name" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Last Name</label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-user"></i>
                                            </span>
                                            <input type="text" class="form-control" id="lastName" 
                                                   placeholder="Last name" required>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Username</label>
                                    <div class="input-group">
                                        <span class="input-group-text">
                                            <i class="fas fa-at"></i>
                                        </span>
                                        <input type="text" class="form-control" id="username" 
                                               placeholder="Choose a username" required>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <div class="input-group">
                                        <span class="input-group-text">
                                            <i class="fas fa-envelope"></i>
                                        </span>
                                        <input type="email" class="form-control" id="email" 
                                               placeholder="Enter your email" required>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Phone Number</label>
                                    <div class="input-group">
                                        <span class="input-group-text">
                                            <i class="fas fa-phone"></i>
                                        </span>
                                        <input type="tel" class="form-control" id="phoneNumber" 
                                               placeholder="Enter your phone number">
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Role</label>
                                    <select class="form-select" id="role" required>
                                        <option value="">Select your role</option>
                                        <option value="customer">Customer - I want to order food</option>
                                        <option value="chef">Chef - I want to sell food</option>
                                    </select>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Password</label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-lock"></i>
                                            </span>
                                            <input type="password" class="form-control" id="password" 
                                                   placeholder="Create a password" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Confirm Password</label>
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-lock"></i>
                                            </span>
                                            <input type="password" class="form-control" id="confirmPassword" 
                                                   placeholder="Confirm your password" required>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3 form-check">
                                    <input type="checkbox" class="form-check-input" id="agreeTerms" required>
                                    <label class="form-check-label" for="agreeTerms">
                                        I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
                                    </label>
                                </div>
                                
                                <button type="submit" class="btn btn-primary w-100">
                                    <i class="fas fa-user-plus me-2"></i>Create Account
                                </button>
                                
                                <div class="text-center mt-3">
                                    <span class="text-muted">Already have an account? </span>
                                    <a href="#" class="text-primary" onclick="switchToLogin()">Login</a>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('authModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('authModal'));
    modal.show();
    
    // Add event listeners
    document.getElementById('loginFormElement').addEventListener('submit', handleLogin);
    document.getElementById('registerFormElement').addEventListener('submit', handleRegister);
}

function switchToRegister() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
    document.querySelector('#authModal .modal-title').textContent = 'Create New Account';
}

function switchToLogin() {
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
    document.querySelector('#authModal .modal-title').textContent = 'Welcome Back!';
}

function showForgotPassword() {
    alert('Password reset functionality coming soon! Please contact support for assistance.');
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store auth token
            localStorage.setItem('authToken', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('authModal')).hide();
            
            // Show success message
            showSuccess('Login successful! Welcome back.');
            
            // Reload page to update UI
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showError(data.non_field_errors ? data.non_field_errors[0] : 'Login failed. Please try again.');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Login failed. Please try again later.');
    }
}

// Handle registration
async function handleRegister(e) {
    e.preventDefault();
    
    const formData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        confirm_password: document.getElementById('confirmPassword').value,
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        phone_number: document.getElementById('phoneNumber').value,
        role: document.getElementById('role').value
    };
    
    // Validate passwords match
    if (formData.password !== formData.confirm_password) {
        showError('Passwords do not match');
        return;
    }
    
    try {
        const response = await fetch('http://127.0.0.1:8000/api/auth/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store auth token
            localStorage.setItem('authToken', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('authModal')).hide();
            
            // Show success message
            showSuccess('Registration successful! Welcome to HomeChefs.');
            
            // Reload page to update UI
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            // Handle validation errors
            if (typeof data === 'object' && data !== null) {
                const errorMessages = Object.keys(data).map(key => 
                    `${key}: ${Array.isArray(data[key]) ? data[key].join(', ') : data[key]}`
                ).join('\n');
                showError(errorMessages);
            } else {
                showError('Registration failed. Please try again.');
            }
        }
    } catch (error) {
        console.error('Registration error:', error);
        showError('Registration failed. Please try again later.');
    }
}

// Show success message
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success position-fixed top-0 start-50 translate-middle-x mt-3';
    successDiv.style.zIndex = '9999';
    successDiv.style.minWidth = '300px';
    successDiv.textContent = message;
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger position-fixed top-0 start-50 translate-middle-x mt-3';
    errorDiv.style.zIndex = '9999';
    errorDiv.style.minWidth = '300px';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}
