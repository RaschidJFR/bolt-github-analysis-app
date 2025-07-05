#!/usr/bin/env python3
"""
Test script for local Flask development
Run this to test the application locally
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if required environment variables are set"""
    print("Testing environment variables...")
    
    github_token = os.getenv('GITHUB_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not github_token:
        print("❌ GITHUB_TOKEN not found in environment")
        print("   Please add it to your .env file")
        return False
    else:
        print("✅ GITHUB_TOKEN found")
    
    if not openai_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("   Please add it to your .env file")
        return False
    else:
        print("✅ OPENAI_API_KEY found")
    
    return True

def test_imports():
    """Test if all required packages can be imported"""
    print("\nTesting imports...")
    
    try:
        from flask import Flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        from ghIssueAnalyzer import IssueAnalyzer, ChatGPT
        print("✅ ghIssueAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ ghIssueAnalyzer import failed: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    return True

def test_flask_app():
    """Test if the Flask app can be created"""
    print("\nTesting Flask app creation...")
    
    try:
        from app import app
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("GitHub Repository Analyzer - Local Test")
    print("=" * 40)
    
    tests = [
        test_environment,
        test_imports,
        test_flask_app
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ All tests passed! You can run the app with:")
        print("   python app.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 