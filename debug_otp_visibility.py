#!/usr/bin/env python
"""
Debug script to check OTP tab visibility issues
"""

import os

def check_otp_visibility():
    """Check for potential issues with OTP tab visibility"""
    
    print("HomeChefs AI - OTP Visibility Debug")
    print("=" * 40)
    
    template_path = "HomeChefs/templates/HomeChefs/base.html"
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check for common visibility issues
        issues = []
        
        # 1. Check for CSS that might hide OTP elements
        if 'display:none' in content.lower() and 'otp' in content.lower():
            issues.append("Found 'display:none' near OTP elements - check CSS")
        
        if 'hidden' in content.lower() and 'otp' in content.lower():
            issues.append("Found 'hidden' near OTP elements - check CSS")
        
        # 2. Check Bootstrap classes
        if 'd-none' in content and 'otp' in content:
            issues.append("Found 'd-none' (Bootstrap hidden) near OTP elements")
        
        # 3. Check tab structure
        otp_tab_start = content.find('id="otp-tab"')
        if otp_tab_start == -1:
            issues.append("OTP tab not found")
        else:
            # Check surrounding context
            context_start = max(0, otp_tab_start - 200)
            context_end = min(len(content), otp_tab_start + 200)
            context = content[context_start:context_end]
            
            print("OTP Tab Context:")
            print("-" * 20)
            print(context)
            print("-" * 20)
        
        # 4. Check OTP login form
        otp_form_start = content.find('id="otp-login"')
        if otp_form_start == -1:
            issues.append("OTP login form not found")
        else:
            # Check surrounding context
            context_start = max(0, otp_form_start - 200)
            context_end = min(len(content), otp_form_start + 200)
            context = content[context_start:context_end]
            
            print("\nOTP Login Form Context:")
            print("-" * 25)
            print(context)
            print("-" * 25)
        
        # 5. Check JavaScript functions
        if 'function sendLoginOTP()' not in content:
            issues.append("sendLoginOTP function not found")
        
        if 'function verifyLoginOTP()' not in content:
            issues.append("verifyLoginOTP function not found")
        
        # 6. Check Bootstrap CSS loading
        if 'bootstrap' not in content.lower():
            issues.append("Bootstrap CSS might not be loaded")
        
        # 7. Check Font Awesome for icons
        if 'font-awesome' not in content.lower() and 'fa-' not in content:
            issues.append("Font Awesome might not be loaded (icons may not show)")
        
        # Report issues
        if issues:
            print("\nPotential Issues Found:")
            print("-" * 25)
            for i, issue in enumerate(issues, 1):
                print(f"{i}. {issue}")
        else:
            print("\nNo obvious visibility issues found in template")
        
        # Provide manual testing steps
        print(f"\nManual Testing Steps:")
        print("-" * 25)
        print("1. Open http://localhost:8000 in browser")
        print("2. Click 'Login' button to open modal")
        print("3. Look for tabs: 'Password' and 'OTP'")
        print("4. If OTP tab not visible:")
        print("   - Press F12 to open developer tools")
        print("   - Check Console for JavaScript errors")
        print("   - Inspect the login modal HTML")
        print("   - Look for CSS that might hide the OTP tab")
        
        print(f"\nBrowser Console Commands:")
        print("-" * 30)
        print("// Check if OTP tab exists")
        print("document.getElementById('otp-tab')")
        print("")
        print("// Check if OTP tab is visible")
        print("const otpTab = document.getElementById('otp-tab');")
        print("otpTab ? window.getComputedStyle(otpTab).display : 'Not found'")
        print("")
        print("// Manually show OTP tab")
        print("const otpTab = document.getElementById('otp-tab');")
        print("if (otpTab) otpTab.style.display = 'block';")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"Error reading template: {e}")
        return False

def create_simple_test_page():
    """Create a simple test page to verify OTP functionality"""
    
    test_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Test - HomeChefs AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>OTP Functionality Test</h1>
        
        <!-- Login Modal Test -->
        <div class="modal show" style="display: block; position: relative;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Login Test</h5>
                    </div>
                    <div class="modal-body">
                        <!-- Login Method Tabs -->
                        <ul class="nav nav-pills nav-justified mb-4" id="loginMethodTabs" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="password-tab" data-bs-toggle="pill" data-bs-target="#password-login" type="button" role="tab">
                                    <i class="fas fa-key me-2"></i>Password
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="otp-tab" data-bs-toggle="pill" data-bs-target="#otp-login" type="button" role="tab">
                                    <i class="fas fa-mobile-alt me-2"></i>OTP
                                </button>
                            </li>
                        </ul>

                        <!-- Tab Content -->
                        <div class="tab-content" id="loginMethodTabContent">
                            <!-- Password Login -->
                            <div class="tab-pane fade show active" id="password-login" role="tabpanel">
                                <form>
                                    <div class="mb-3">
                                        <label class="form-label">Username</label>
                                        <input type="text" class="form-control" placeholder="Enter username">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Password</label>
                                        <input type="password" class="form-control" placeholder="Enter password">
                                    </div>
                                </form>
                            </div>

                            <!-- OTP Login -->
                            <div class="tab-pane fade" id="otp-login" role="tabpanel">
                                <form>
                                    <div class="mb-3">
                                        <label class="form-label">Phone Number</label>
                                        <div class="input-group">
                                            <span class="input-group-text"><i class="fas fa-mobile-alt"></i></span>
                                            <input type="tel" class="form-control" placeholder="Enter your phone number">
                                            <button class="btn btn-outline-secondary" type="button">Send OTP</button>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Verification Code</label>
                                        <div class="input-group">
                                            <span class="input-group-text"><i class="fas fa-shield-alt"></i></span>
                                            <input type="text" class="form-control" placeholder="Enter 6-digit code" maxlength="6">
                                            <button class="btn btn-primary" type="button">Login with OTP</button>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-4">
            <h3>Test Results:</h3>
            <div id="testResults">
                <p>Testing OTP tab visibility...</p>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Test OTP tab visibility
        document.addEventListener('DOMContentLoaded', function() {
            const otpTab = document.getElementById('otp-tab');
            const otpLogin = document.getElementById('otp-login');
            const results = document.getElementById('testResults');
            
            let testResults = [];
            
            if (otpTab) {
                testResults.push('✓ OTP tab found');
                const style = window.getComputedStyle(otpTab);
                testResults.push(`✓ OTP tab display: ${style.display}`);
                testResults.push(`✓ OTP tab visibility: ${style.visibility}`);
            } else {
                testResults.push('✗ OTP tab NOT found');
            }
            
            if (otpLogin) {
                testResults.push('✓ OTP login form found');
            } else {
                testResults.push('✗ OTP login form NOT found');
            }
            
            // Test tab switching
            const passwordTab = document.getElementById('password-tab');
            if (passwordTab && otpTab) {
                testResults.push('✓ Both tabs found - switching should work');
                
                // Add click handlers for testing
                otpTab.addEventListener('click', function() {
                    testResults.push('✓ OTP tab clicked');
                    results.innerHTML = testResults.map(r => `<p>${r}</p>`).join('');
                });
                
                passwordTab.addEventListener('click', function() {
                    testResults.push('✓ Password tab clicked');
                    results.innerHTML = testResults.map(r => `<p>${r}</p>`).join('');
                });
            }
            
            results.innerHTML = testResults.map(r => `<p>${r}</p>`).join('');
        });
    </script>
</body>
</html>'''
    
    with open('otp_test.html', 'w') as f:
        f.write(test_html)
    
    print("Created otp_test.html - open in browser to test OTP tab visibility")

if __name__ == '__main__':
    is_ok = check_otp_visibility()
    
    if not is_ok:
        print("\nCreating test page for further debugging...")
        create_simple_test_page()
        print("Open otp_test.html in your browser to test OTP visibility")
