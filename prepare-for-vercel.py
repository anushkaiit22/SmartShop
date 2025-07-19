#!/usr/bin/env python3
"""
Prepare for Vercel Deployment Script
Combines compatibility testing and Render cleanup
"""

import sys
import os
import subprocess

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    # Remove emoji characters for Windows compatibility
    title = title.encode('ascii', 'ignore').decode('ascii')
    print(f"[START] {title}")
    print("=" * 60)

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print_header(description)
    
    if not os.path.exists(script_name):
        print(f"❌ Script {script_name} not found!")
        return False
    
    try:
        # Run the script using subprocess to capture output
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=300)
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"⚠️  Warnings/Errors: {result.stderr}")
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def main():
    """Main function"""
    print_header("SmartShop Vercel Deployment Preparation")
    
    print("This script will:")
    print("1. [CLEAN] Clean up Render-specific files and configurations")
    print("2. [TEST] Test Vercel compatibility")
    print("3. [INFO] Provide deployment recommendations")
    
    # Ask for confirmation
    response = input("\nDo you want to continue? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Preparation cancelled.")
        return
    
    success_count = 0
    total_steps = 2
    
    # Step 1: Cleanup Render files
    if run_script("cleanup-render-files.py", "Cleaning up Render files"):
        success_count += 1
    
    # Step 2: Test Vercel compatibility
    if run_script("test-vercel-compatibility.py", "Testing Vercel compatibility"):
        success_count += 1
    
    # Summary
    print_header("Preparation Summary")
    
    if success_count == total_steps:
        print("[SUCCESS] All steps completed successfully!")
        print("\n[NEXT] Next Steps:")
        print("1. Review the test results above")
        print("2. Fix any errors or warnings if needed")
        print("3. Run the deployment scripts:")
        print("   - Windows: deploy-vercel.bat")
        print("   - Unix/Linux: ./deploy-vercel.sh")
        print("4. Or deploy manually using Vercel dashboard")
        print("\n[DOCS] See VERCEL_DEPLOYMENT.md for detailed instructions")
    else:
        print(f"[WARNING] {total_steps - success_count} step(s) failed.")
        print("Please review the errors above and fix them before deploying.")
        print("\n[TIPS] Common issues:")
        print("- Missing dependencies: pip install -r requirements-vercel.txt")
        print("- Import errors: Check that all modules are available")
        print("- Configuration issues: Review app/core/config.py")

if __name__ == "__main__":
    main() 