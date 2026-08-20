#!/usr/bin/env python
"""
Check Bootstrap version and potential conflicts
"""

import os
import re

def check_bootstrap_version():
    """Check Bootstrap version in template"""
    
    template_path = "HomeChefs/templates/HomeChefs/base.html"
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        print("Bootstrap Version Check:")
        print("=" * 25)
        
        # Find Bootstrap CSS
        bootstrap_css = re.findall(r'bootstrap[^"\']*\.css', content, re.IGNORECASE)
        print("Bootstrap CSS files found:")
        for css in bootstrap_css:
            print(f"  - {css}")
        
        # Find Bootstrap JS
        bootstrap_js = re.findall(r'bootstrap[^"\']*\.js', content, re.IGNORECASE)
        print("\nBootstrap JS files found:")
        for js in bootstrap_js:
            print(f"  - {js}")
        
        # Check for version numbers
        versions = re.findall(r'bootstrap[\/\-]?(\d+\.[\d\.]+)', content, re.IGNORECASE)
        if versions:
            print(f"\nBootstrap versions detected: {versions}")
        else:
            print("\nNo explicit Bootstrap version detected")
        
        # Check for potential conflicts
        conflicts = []
        
        # Check for multiple Bootstrap versions
        if len(set(bootstrap_css + bootstrap_js)) > 2:
            conflicts.append("Multiple Bootstrap files detected")
        
        # Check for conflicting CSS frameworks
        if 'tailwind' in content.lower():
            conflicts.append("Tailwind CSS detected - may conflict with Bootstrap")
        
        if 'foundation' in content.lower():
            conflicts.append("Foundation CSS detected - may conflict with Bootstrap")
        
        # Check for custom CSS that might hide elements
        if 'display:none' in content.lower():
            conflicts.append("Found 'display:none' in template")
        
        if 'visibility:hidden' in content.lower():
            conflicts.append("Found 'visibility:hidden' in template")
        
        if conflicts:
            print(f"\nPotential conflicts found:")
            for conflict in conflicts:
                print(f"  - {conflict}")
        else:
            print(f"\nNo obvious conflicts detected")
        
        return True
        
    except Exception as e:
        print(f"Error checking Bootstrap: {e}")
        return False

def create_minimal_working_example():
    """Create a minimal working example of OTP tabs"""
    
    minimal_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minimal OTP Test</title>
    <!-- Bootstrap 5.3.0 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        /* Debug styles */
        .debug-border {
            border: 2px solid red !important;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1>Minimal OTP Working Example</h1>
        
        <!-- Simple Modal -->
        <div class="modal show" style="display: block; position: relative;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Login</h5>
                    </div>
                    <div class="modal-body">
                        <!-- Tabs -->
                        <ul class="nav nav-pills nav-justified mb-4">
                            <li class="nav-item">
                                <button class="nav-link active" data-bs-toggle="pill" data-bs-target="#password-tab-content">
                                    Password
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link debug-border" data-bs-toggle="pill" data-bs-target="#otp-tab-content">
                                    OTP
                                </button>
                            </li>
                        </ul>
                        
                        <!-- Tab Content -->
                        <div class="tab-content">
                            <div class="tab-pane fade show active" id="password-tab-content">
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
                            
                            <div class="tab-pane fade" id="otp-tab-content">
                                <form>
                                    <div class="mb-3">
                                        <label class="form-label">Phone Number</label>
                                        <input type="tel" class="form-control" placeholder="Enter phone number">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">OTP Code</label>
                                        <input type="text" class="form-control" placeholder="Enter OTP">
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
            <div id="results">
                <p>Testing...</p>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const results = document.getElementById('results');
            const otpTab = document.querySelector('[data-bs-target="#otp-tab-content"]');
            const otpContent = document.getElementById('otp-tab-content');
            
            let output = [];
            
            output.push('OTP Tab Element Found: ' + (!!otpTab));
            output.push('OTP Content Found: ' + (!!otpContent));
            
            if (otpTab) {
                const style = window.getComputedStyle(otpTab);
                output.push('OTP Tab Display: ' + style.display);
                output.push('OTP Tab Visibility: ' + style.visibility);
                output.push('OTP Tab Opacity: ' + style.opacity);
            }
            
            if (otpContent) {
                const style = window.getComputedStyle(otpContent);
                output.push('OTP Content Display: ' + style.display);
                output.push('OTP Content Visibility: ' + style.visibility);
            }
            
            // Test tab switching
            if (otpTab) {
                otpTab.addEventListener('click', function() {
                    output.push('OTP Tab Clicked - Bootstrap should handle switching');
                    results.innerHTML = output.map(o => '<p>' + o + '</p>').join('');
                });
            }
            
            results.innerHTML = output.map(o => '<p>' + o + '</p>').join('');
        });
    </script>
</body>
</html>'''
    
    with open('minimal_otp_test.html', 'w') as f:
        f.write(minimal_html)
    
    print("Created minimal_otp_test.html")

if __name__ == '__main__':
    print("HomeChefs AI - Bootstrap Check")
    print("=" * 30)
    
    check_bootstrap_version()
    create_minimal_working_example()
    
    print("\nTesting Steps:")
    print("1. Open minimal_otp_test.html - should show RED bordered OTP tab")
    print("2. If minimal test works, issue is in main template")
    print("3. Check main site for RED bordered OTP tab")
    print("4. If still not visible, may need to check browser compatibility")
