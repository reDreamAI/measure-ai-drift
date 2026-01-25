#!/usr/bin/env python3
"""Quick test to verify CLI setup is correct."""

import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, description):
    """Run command and check if it works."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✓ {description}")
            return True
        else:
            error = result.stderr[:100] if result.stderr else "unknown error"
            print(f"✗ {description}")
            print(f"  Error: {error}")
            return False
    except Exception as e:
        print(f"✗ {description}")
        print(f"  Error: {str(e)[:100]}")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("CLI Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("python3 --version", "Python 3 available"),
        ("python3 -m src --help", "CLI works with python3 -m src"),
        ("./run --help", "Wrapper script works"),
        ("python3 -m src list-vignettes", "list-vignettes command"),
    ]
    
    results = []
    for cmd, desc in checks:
        print(f"Testing: {desc}...")
        result = run_cmd(cmd, desc)
        results.append(result)
        print()
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print()
    
    if passed == total:
        print("🎉 All checks passed! You can now run:")
        print()
        print("  python3 -m src generate")
        print("  ./run generate")
        print("  python -m src generate  (after setting alias)")
        print()
    else:
        print("⚠️  Some checks failed. See errors above.")
        print()
        print("Fix with:")
        print("  1. pip install -r requirements.txt")
        print("  2. python3 -m src list-vignettes")
        print()
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
