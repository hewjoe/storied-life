#!/usr/bin/env python3
"""
OIDC Authentication Test Runner for Storied Life

This script provides convenient commands to run different types of authentication tests.

Usage:
    python scripts/run_auth_tests.py [command] [options]

Commands:
    config     - Run configuration validation tests
    unit       - Run unit tests only (fast)
    integration- Run integration tests (requires connectivity)
    all        - Run all authentication tests
    quick      - Run quick validation script + unit tests
"""

import sys
import subprocess
import asyncio
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_command(cmd: list, description: str = ""):
    """Run a command and return the result."""
    print(f"\n🚀 {description}")
    print(f"📝 Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def run_config_validation():
    """Run configuration validation script."""
    print("🔍 Running OIDC Configuration Validation...")
    
    try:
        # Import and run the validation script
        import asyncio
        from scripts.validate_oidc_config import main
        
        # Run the async validation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(main())
            return True
        except SystemExit as e:
            return e.code == 0
        finally:
            loop.close()
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def run_unit_tests():
    """Run unit tests only."""
    return run_command(
        ["python", "-m", "pytest", "tests/test_oidc_auth.py", "-m", "unit", "-v"],
        "Running Unit Tests"
    )

def run_integration_tests():
    """Run integration tests."""
    return run_command(
        ["python", "-m", "pytest", "tests/test_oidc_auth.py", "-m", "integration", "-v"],
        "Running Integration Tests"
    )

def run_config_tests():
    """Run configuration validation tests."""
    return run_command(
        ["python", "-m", "pytest", "tests/test_oidc_auth.py", "-m", "config", "-v"],
        "Running Configuration Tests"
    )

def run_all_tests():
    """Run all authentication tests."""
    return run_command(
        ["python", "-m", "pytest", "tests/test_oidc_auth.py", "-v"],
        "Running All Authentication Tests"
    )

def run_quick_validation():
    """Run quick validation: config script + unit tests."""
    print("⚡ Running Quick Validation (Config + Unit Tests)")
    
    config_ok = run_config_validation()
    unit_ok = run_unit_tests()
    
    if config_ok and unit_ok:
        print("\n🎉 Quick validation passed! Your OIDC configuration looks good.")
        return True
    else:
        print("\n❌ Quick validation failed. Check the errors above.")
        return False

def print_usage():
    """Print usage information."""
    print(__doc__)

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    success = False
    
    if command == "config":
        success = run_config_validation()
    elif command == "unit":
        success = run_unit_tests()
    elif command == "integration":
        success = run_integration_tests()
    elif command == "all":
        success = run_all_tests()
    elif command == "quick":
        success = run_quick_validation()
    elif command in ["help", "-h", "--help"]:
        print_usage()
        success = True
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 