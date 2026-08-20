#!/usr/bin/env python
"""
Force OTP tab to be visible with more aggressive fixes
"""

import os

def force_otp_visible():
    """Apply more aggressive OTP visibility fixes"""
    
    template_path = "HomeChefs/templates/HomeChefs/base.html"
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Add more aggressive CSS fix
        aggressive_css = '''
    <!-- Aggressive OTP Visibility Fix -->
    <style>
        /* Force OTP tab visibility with higher specificity */
        body div.modal div.modal-content div.modal-body ul.nav-pills li.nav-item button#otp-tab {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            position: relative !important;
            z-index: 1000 !important;
            width: auto !important;
            height: auto !important;
        }
        
        /* Force OTP login form visibility */
        body div.modal div.modal-content div.modal-body div.tab-content div#otp-login {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        
        /* Ensure nav pills are visible */
        .nav-pills .nav-link {
            display: inline-block !important;
            visibility: visible !important;
            min-width: 80px;
            text-align: center;
        }
        
        /* Debug border to see if element exists */
        #otp-tab {
            border: 2px solid red !important;
            background-color: yellow !important;
        }
        
        #otp-login {
            border: 2px solid blue !important;
        }
    </style>
'''
        
        # Add immediate JavaScript fix that runs before anything else
        immediate_js = '''
    <!-- Immediate OTP Fix -->
    <script>
        // Run immediately when DOM is ready
        (function() {
            function fixOTP() {
                console.log('Running OTP fix...');
                
                // Find OTP tab
                const otpTab = document.getElementById('otp-tab');
                const otpLogin = document.getElementById('otp-login');
                const passwordTab = document.getElementById('password-tab');
                const passwordLogin = document.getElementById('password-login');
                
                console.log('OTP tab found:', !!otpTab);
                console.log('OTP login found:', !!otpLogin);
                console.log('Password tab found:', !!passwordTab);
                console.log('Password login found:', !!passwordLogin);
                
                if (otpTab) {
                    // Force visibility
                    otpTab.style.display = 'block';
                    otpTab.style.visibility = 'visible';
                    otpTab.style.opacity = '1';
                    otpTab.style.position = 'relative';
                    otpTab.style.zIndex = '1000';
                    
                    // Remove any hidden classes
                    otpTab.classList.remove('d-none', 'hidden', 'invisible');
                    
                    console.log('OTP tab forced visible');
                }
                
                if (otpLogin) {
                    otpLogin.style.display = 'block';
                    otpLogin.style.visibility = 'visible';
                    otpLogin.style.opacity = '1';
                    otpLogin.classList.remove('d-none', 'hidden', 'invisible');
                    console.log('OTP login forced visible');
                }
                
                // Setup proper tab switching
                if (otpTab && passwordTab) {
                    // Remove existing handlers
                    const newOtpTab = otpTab.cloneNode(true);
                    otpTab.parentNode.replaceChild(newOtpTab, otpTab);
                    
                    const newPasswordTab = passwordTab.cloneNode(true);
                    passwordTab.parentNode.replaceChild(newPasswordTab, passwordTab);
                    
                    // Add new handlers
                    newOtpTab.addEventListener('click', function(e) {
                        e.preventDefault();
                        console.log('OTP tab clicked');
                        
                        // Switch forms
                        if (otpLogin) {
                            otpLogin.classList.add('show', 'active');
                            otpLogin.style.display = 'block';
                        }
                        if (passwordLogin) {
                            passwordLogin.classList.remove('show', 'active');
                            passwordLogin.style.display = 'none';
                        }
                        
                        // Switch tabs
                        newOtpTab.classList.add('active');
                        newPasswordTab.classList.remove('active');
                    });
                    
                    newPasswordTab.addEventListener('click', function(e) {
                        e.preventDefault();
                        console.log('Password tab clicked');
                        
                        // Switch forms
                        if (passwordLogin) {
                            passwordLogin.classList.add('show', 'active');
                            passwordLogin.style.display = 'block';
                        }
                        if (otpLogin) {
                            otpLogin.classList.remove('show', 'active');
                            otpLogin.style.display = 'none';
                        }
                        
                        // Switch tabs
                        newPasswordTab.classList.add('active');
                        newOtpTab.classList.remove('active');
                    });
                }
            }
            
            // Try multiple times to ensure it runs
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', fixOTP);
            } else {
                fixOTP();
            }
            
            // Also try after a delay
            setTimeout(fixOTP, 100);
            setTimeout(fixOTP, 500);
            setTimeout(fixOTP, 1000);
        })();
    </script>
'''
        
        # Find where to insert CSS (before closing </head> tag)
        head_end = content.find('</head>')
        if head_end != -1:
            content = content[:head_end] + aggressive_css + '\n' + content[head_end:]
        
        # Find where to insert JavaScript (in <head> to run early)
        head_insert = content.find('<meta charset="UTF-8">')
        if head_insert != -1:
            insert_pos = content.find('\n', head_insert) + 1
            content = content[:insert_pos] + immediate_js + '\n' + content[insert_pos:]
        
        # Write the updated content
        with open(template_path, 'w') as f:
            f.write(content)
        
        print("Aggressive OTP visibility fix applied!")
        print("\nChanges made:")
        print("1. Added high-specificity CSS with debug borders")
        print("2. Added immediate JavaScript that runs multiple times")
        print("3. Added debug logging and visual indicators")
        print("4. Forced tab switching with new event handlers")
        
        print("\nDebug features added:")
        print("- OTP tab will have RED border")
        print("- OTP login form will have BLUE border")
        print("- Console will show detailed logs")
        
        print("\nTo test:")
        print("1. Clear browser cache (Ctrl+Shift+Del)")
        print("2. Refresh the page")
        print("3. Open login modal")
        print("4. Look for RED bordered OTP tab")
        print("5. Press F12 to see console logs")
        
    except Exception as e:
        print(f"Error applying fix: {e}")

def create_simple_otp_test():
    """Create a minimal OTP test to isolate the issue"""
    
    simple_test = '''<!DOCTYPE html>
<html>
<head>
    <title>Simple OTP Test</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        #otp-tab {
            border: 3px solid red !important;
            background: yellow !important;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1>Simple OTP Test</h1>
        
        <div class="card">
            <div class="card-body">
                <ul class="nav nav-pills nav-justified mb-4">
                    <li class="nav-item">
                        <button class="nav-link active" id="password-tab">Password</button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link" id="otp-tab">OTP</button>
                    </li>
                </ul>
                
                <div class="tab-content">
                    <div class="tab-pane show active" id="password-login">
                        <p>Password login form</p>
                    </div>
                    <div class="tab-pane" id="otp-login">
                        <p>OTP login form</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-3">
            <h3>Debug Info:</h3>
            <div id="debug"></div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const otpTab = document.getElementById('otp-tab');
            const debug = document.getElementById('debug');
            
            debug.innerHTML = 'OTP tab found: ' + (!!otpTab) + '<br>';
            
            if (otpTab) {
                const style = window.getComputedStyle(otpTab);
                debug.innerHTML += 'Display: ' + style.display + '<br>';
                debug.innerHTML += 'Visibility: ' + style.visibility + '<br>';
                debug.innerHTML += 'Opacity: ' + style.opacity + '<br>';
            }
        });
    </script>
</body>
</html>'''
    
    with open('simple_otp_test.html', 'w') as f:
        f.write(simple_test)
    
    print("Created simple_otp_test.html - open in browser to test basic OTP tab")

if __name__ == '__main__':
    print("HomeChefs AI - Force OTP Visible")
    print("=" * 35)
    
    force_otp_visible()
    create_simple_otp_test()
    
    print("\nNext steps:")
    print("1. Open simple_otp_test.html first - if OTP tab shows, issue is in main site")
    print("2. Check main site for RED bordered OTP tab")
    print("3. Look at console logs for debugging info")
    print("4. If still not visible, the issue might be in Bootstrap version or CSS conflicts")
