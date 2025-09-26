#!/usr/bin/env python3
"""
MedicLab Development Environment Verification Script
This script verifies that the development environment is properly configured.
"""

import sys
import os
import subprocess
import platform

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python version requirement met (3.8+)")
        return True
    else:
        print("✗ Python version requirement not met (need 3.8+)")
        return False

def check_node_version():
    """Check if Node.js version is 16 or higher"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version_str = result.stdout.strip()
        version_num = int(version_str.replace('v', '').split('.')[0])
        
        print(f"Node.js version: {version_str}")
        
        if version_num >= 16:
            print("✓ Node.js version requirement met (16+)")
            return True
        else:
            print("✗ Node.js version requirement not met (need 16+)")
            return False
    except Exception as e:
        print(f"✗ Node.js not found or error checking version: {e}")
        return False

def check_npm():
    """Check if npm is available"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        version_str = result.stdout.strip()
        print(f"npm version: {version_str}")
        print("✓ npm is available")
        return True
    except Exception as e:
        print(f"✗ npm not found or error: {e}")
        return False

def check_directory_structure():
    """Check if the project directory structure exists"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_dirs = [
        'backend',
        'frontend',
        'backend/venv'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = os.path.join(base_dir, dir_path)
        if os.path.exists(full_path):
            print(f"✓ Directory exists: {dir_path}")
        else:
            print(f"✗ Directory missing: {dir_path}")
            all_exist = False
    
    return all_exist

def check_virtual_environment():
    """Check if Python virtual environment is properly configured"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(base_dir, 'backend', 'venv')
    
    if platform.system() == 'Windows':
        python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
        activate_script = os.path.join(venv_path, 'Scripts', 'Activate.ps1')
    else:
        python_exe = os.path.join(venv_path, 'bin', 'python')
        activate_script = os.path.join(venv_path, 'bin', 'activate')
    
    if os.path.exists(python_exe):
        print("✓ Virtual environment Python executable found")
        venv_ok = True
    else:
        print("✗ Virtual environment Python executable not found")
        venv_ok = False
    
    if os.path.exists(activate_script):
        print("✓ Virtual environment activation script found")
    else:
        print("✗ Virtual environment activation script not found")
        venv_ok = False
    
    return venv_ok

def main():
    """Main verification function"""
    print("MedicLab Development Environment Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Node.js Version", check_node_version),
        ("npm Availability", check_npm),
        ("Directory Structure", check_directory_structure),
        ("Virtual Environment", check_virtual_environment)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    
    if all(results):
        print("✓ All checks passed! Development environment is ready.")
        return 0
    else:
        print("✗ Some checks failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())