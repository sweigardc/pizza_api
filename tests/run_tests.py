#!/usr/bin/env python3
"""
Simple Test Runner for Pizza API
This script runs comprehensive tests without external dependencies.
"""

import os
import sys

def main():
    """Run the comprehensive pizza API tests"""
    print("🚀 STARTING PIZZA API COMPREHENSIVE TESTS")
    print("=" * 50)
    
    try:
        # Change to project directory
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_dir)
        
        print(f"📁 Running tests from: {project_dir}")
        print("📝 Test phases:")
        print("   1. Populate ingredient test data")
        print("   2. Populate pizza test data")
        print("   3. Test ingredient CRUD endpoints")
        print("   4. Test pizza CRUD endpoints")
        print("   5. Test advanced features (search, sort, filter)")
        print("   6. Test error handling")
        print("\n" + "-" * 50)
        
        # Run the comprehensive tests
        exit_code = os.system("python tests/test_pizza_comprehensive.py")
        
        if exit_code == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("Your Pizza API is working perfectly!")
        else:
            print("\n❌ SOME TESTS FAILED")
            print("Check the output above for details.")
            
        return exit_code == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        return False

def show_test_info():
    """Show information about what the tests do"""
    print("📋 PIZZA API TEST SUITE INFORMATION")
    print("=" * 50)
    print("\n🧄 INGREDIENT TESTS:")
    print("   • Create comprehensive ingredient data (base + allergens)")
    print("   • Test CREATE ingredient endpoint")
    print("   • Test READ all ingredients endpoint")
    print("   • Test READ single ingredient endpoint")
    print("   • Test UPDATE ingredient endpoint")
    print("   • Test DELETE ingredient endpoint")
    
    print("\n🍕 PIZZA TESTS:")
    print("   • Create diverse pizza data (8+ different pizzas)")
    print("   • Test CREATE pizza endpoint")
    print("   • Test READ all pizzas endpoint")
    print("   • Test READ single pizza endpoint")
    print("   • Test UPDATE pizza endpoint")
    print("   • Test DELETE pizza endpoint")
    
    print("\n🔍 ADVANCED FEATURE TESTS:")
    print("   • Search pizzas by name and description")
    print("   • Sort pizzas alphabetically")
    print("   • Filter pizzas by ingredients")
    print("   • Test pagination (limit/page parameters)")
    
    print("\n❌ ERROR HANDLING TESTS:")
    print("   • Invalid data validation")
    print("   • Non-existent resource errors (404)")
    print("   • Business logic errors (400)")
    
    print("\n📊 TEST DATA CREATED:")
    print("   • 15+ ingredients (including allergens)")
    print("   • 8+ pizzas (classic varieties)")
    print("   • Comprehensive test scenarios")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        show_test_info()
    else:
        success = main()
        if not success:
            sys.exit(1)