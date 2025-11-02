#!/usr/bin/env python3
"""
Test runner for Kubernetes deployment
Runs tests against the deployed pizza API and PostgreSQL database
Make sure ports are forwarded before running this script:
    kubectl port-forward svc/pizza-api-service 8080:80 &
    kubectl port-forward svc/postgres-service 5433:5432 &
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def setup_test_environment():
    """Set up environment variables for testing against Kubernetes"""

    print("🔧 Setting up test environment for Kubernetes...")
    
    # Database connection (through port-forward)
    os.environ['POSTGRES_HOSTNAME'] = 'localhost'
    os.environ['DATABASE_PORT'] = '5433'
    os.environ['POSTGRES_DB'] = 'pizza_api'
    os.environ['POSTGRES_USER'] = 'pizza_user'
    os.environ['POSTGRES_PASSWORD'] = 'pizza_password'
    
    print("✅ Environment configured for Kubernetes testing")
    print(f"   Database: {os.environ['POSTGRES_HOSTNAME']}:{os.environ['DATABASE_PORT']}")

def check_port_forwards():
    """Check if required port forwards are active"""
    print("\n🔌 Checking port forwards...")
    
    # Check if kubectl port-forward processes are running
    try:
        result = subprocess.run(['pgrep', '-f', 'kubectl port-forward'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Port-forward processes found")
            
            # List active port forwards
            ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            for line in ps_result.stdout.split('\n'):
                if 'kubectl port-forward' in line and ('pizza-api' in line or 'postgres' in line):
                    print(f"   📡 {line.split()[-1]}")
            return True
        else:
            print("❌ No port-forward processes found")
            return False
    except Exception as e:
        print(f"⚠️  Could not check port-forward status: {e}")
        return True  # Continue anyway

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running test suite against Kubernetes deployment...")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Run the comprehensive tests using the existing test runner
    try:
        result = subprocess.run([
            sys.executable, 'run_tests.py'
        ], capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def show_port_forward_commands():
    """Show the required port-forward commands"""
    print("\n📋 Required port-forward commands:")
    print("   kubectl port-forward svc/pizza-api-service 8080:80 &")
    print("   kubectl port-forward svc/postgres-service 5433:5432 &")
    print("\n💡 These should be running in background terminals")

def main():
    """Main test execution"""
    print("🚀 Kubernetes Test Runner for Pizza API")
    print("=" * 50)
    
    # Setup environment
    setup_test_environment()
    
    # Check port forwards
    if not check_port_forwards():
        print("\n❌ Port forwards not detected. Please run:")
        show_port_forward_commands()
        print("\n⚠️  Continuing anyway - tests will fail if ports aren't forwarded")
    
    # Wait a moment for everything to be ready
    print("\n⏳ Waiting 2 seconds for services to be ready...")
    time.sleep(2)
    
    # Run tests
    success = run_tests()
    
    if success:
        print("\n🎉 Kubernetes deployment tests completed successfully!")
        print("   Your pizza API is working correctly in Kubernetes!")
        return 0
    else:
        print("\n💥 Some tests failed. Check output above for details.")
        print("\n🔍 Common issues:")
        print("   • Port forwards not running (see commands above)")
        print("   • Database not ready (wait a few seconds and retry)")
        print("   • Network connectivity issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())