#!/usr/bin/env python
"""
Fix OTP visibility issues
"""

import os

def fix_otp_visibility():
    """Add CSS and JavaScript fixes for OTP visibility"""
    
    template_path = "HomeChefs/templates/HomeChefs/base.html"
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check if fix is already applied
        if 'otp-visibility-fix' in content:
            print("OTP visibility fix already applied")
            return
        
        # Add CSS fix for OTP tab visibility
        css_fix = '''
    <!-- OTP Visibility Fix -->
    <style>
        .otp-visibility-fix {
            display: block !important;
            visibility: visible !important;
        }
        
        #otp-tab {
            display: block !important;
            visibility: visible !important;
        }
        
        #otp-login {
            display: block !important;
            visibility: visible !important;
        }
        
        .nav-pills .nav-link {
            min-width: 100px;
        }
    </style>
'''
        
        # Add JavaScript fix for OTP tab initialization
        js_fix = '''
    <!-- OTP JavaScript Fix -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Ensure OTP tab is visible
            const otpTab = document.getElementById('otp-tab');
            const otpLogin = document.getElementById('otp-login');
            
            if (otpTab) {
                otpTab.style.display = 'block';
                otpTab.style.visibility = 'visible';
                console.log('OTP tab visibility fixed');
            }
            
            if (otpLogin) {
                otpLogin.style.display = 'block';
                otpLogin.style.visibility = 'visible';
                console.log('OTP login form visibility fixed');
            }
            
            // Add click handler to ensure tab switching works
            const otpTabButton = document.getElementById('otp-tab');
            if (otpTabButton) {
                otpTabButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('OTP tab clicked');
                    
                    // Show OTP login form
                    const otpLoginForm = document.getElementById('otp-login');
                    const passwordLoginForm = document.getElementById('password-login');
                    
                    if (otpLoginForm) {
                        otpLoginForm.classList.add('show', 'active');
                    }
                    if (passwordLoginForm) {
                        passwordLoginForm.classList.remove('show', 'active');
                    }
                    
                    // Update tab states
                    document.getElementById('otp-tab').classList.add('active');
                    document.getElementById('password-tab').classList.remove('active');
                });
            }
            
            // Add click handler for password tab
            const passwordTabButton = document.getElementById('password-tab');
            if (passwordTabButton) {
                passwordTabButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('Password tab clicked');
                    
                    // Show password login form
                    const passwordLoginForm = document.getElementById('password-login');
                    const otpLoginForm = document.getElementById('otp-login');
                    
                    if (passwordLoginForm) {
                        passwordLoginForm.classList.add('show', 'active');
                    }
                    if (otpLoginForm) {
                        otpLoginForm.classList.remove('show', 'active');
                    }
                    
                    // Update tab states
                    document.getElementById('password-tab').classList.add('active');
                    document.getElementById('otp-tab').classList.remove('active');
                });
            }
        });
    </script>
'''
        
        # Find where to insert CSS (before closing </head> tag)
        head_end = content.find('</head>')
        if head_end != -1:
            content = content[:head_end] + css_fix + '\n' + content[head_end:]
        
        # Find where to insert JavaScript (before closing </body> tag)
        body_end = content.find('</body>')
        if body_end != -1:
            content = content[:body_end] + js_fix + '\n' + content[body_end:]
        
        # Write the updated content
        with open(template_path, 'w') as f:
            f.write(content)
        
        print("OTP visibility fix applied successfully!")
        print("\nChanges made:")
        print("1. Added CSS to ensure OTP tab visibility")
        print("2. Added JavaScript to handle tab switching")
        print("3. Added console logging for debugging")
        
        print("\nTo test:")
        print("1. Refresh your browser page")
        print("2. Open login modal")
        print("3. Check if OTP tab is now visible")
        print("4. Press F12 to see console logs")
        
    except Exception as e:
        print(f"Error applying fix: {e}")

def check_otp_after_fix():
    """Check OTP status after applying fix"""
    
    print("\nPost-Fix OTP Status Check:")
    print("=" * 30)
    
    template_path = "HomeChefs/templates/HomeChefs/base.html"
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        checks = [
            ('otp-visibility-fix CSS', 'otp-visibility-fix' in content),
            ('OTP tab CSS fix', '#otp-tab' in content and '!important' in content),
            ('OTP JavaScript fix', 'OTP tab clicked' in content),
            ('OTP login form fix', 'OTP login form visibility fixed' in content)
        ]
        
        for check_name, result in checks:
            status = "FOUND" if result else "NOT FOUND"
            print(f"{check_name}: {status}")
        
        print("\nIf OTP is still not visible:")
        print("1. Clear browser cache and refresh")
        print("2. Check browser console for errors")
        print("3. Try opening otp_test.html in browser")
        
    except Exception as e:
        print(f"Error checking fix: {e}")

if __name__ == '__main__':
    print("HomeChefs AI - OTP Visibility Fix")
    print("=" * 40)
    
    fix_otp_visibility()
    check_otp_after_fix()
