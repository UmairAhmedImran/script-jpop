#!/usr/bin/env python3
"""
Test script to verify environment variables are properly set.
Run this before using the main scraper to ensure your configuration is correct.
"""

import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded environment variables from .env file")
except ImportError:
    print("⚠ python-dotenv not installed. Using system environment variables only.")
    print("  Install with: pip install python-dotenv")

def test_env_vars():
    """Test if all required environment variables are set."""
    
    print("\n" + "="*50)
    print("ENVIRONMENT VARIABLE TEST")
    print("="*50)
    
    # Required variables
    required_vars = {
        'JPOPSUKI_USERNAME': 'Your JPopsuki username',
        'JPOPSUKI_PASSWORD': 'Your JPopsuki password'
    }
    
    # Optional variables
    optional_vars = {
        'JPOPSUKI_SEARCH_STRING': 'Search keywords',
        'JPOPSUKI_TAGS': 'Comma-separated tags',
        'JPOPSUKI_CATEGORIES': 'Comma-separated category numbers (1-10)',
        'JPOPSUKI_ORDER': 'Sort order (asc/desc)'
    }
    
    print("\nREQUIRED VARIABLES:")
    all_required_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * len(value)} (hidden)")
        else:
            print(f"✗ {var}: NOT SET - {description}")
            all_required_set = False
    
    print("\nOPTIONAL VARIABLES:")
    for var, description in optional_vars.items():
        value = os.getenv(var, "")
        if value:
            print(f"✓ {var}: '{value}'")
        else:
            print(f"- {var}: not set (will use default) - {description}")
    
    print("\n" + "="*50)
    if all_required_set:
        print("✓ ALL REQUIRED VARIABLES ARE SET!")
        print("You can now run: python sel.py")
    else:
        print("✗ MISSING REQUIRED VARIABLES!")
        print("Please set the missing variables and try again.")
        print("\nOptions:")
        print("1. Create a .env file with your variables")
        print("2. Export variables in your shell")
        print("3. Set them when running the script")
    print("="*50)
    
    return all_required_set

if __name__ == "__main__":
    test_env_vars()
