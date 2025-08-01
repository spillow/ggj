#!/usr/bin/env python3
"""
End-to-end test runner for the game.

This script finds all .txt files in the tools directory and runs them through
the FileCheck tool to verify game functionality.
"""

import os
import sys
import glob
from filecheck import run_filecheck


def find_test_files(directory: str) -> list[str]:
    """Find all .txt test files in the given directory."""
    pattern = os.path.join(directory, "*.txt")
    return glob.glob(pattern)


def main():
    """Run all end-to-end tests."""
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = find_test_files(tools_dir)
    
    if not test_files:
        print("No test files found in tools directory")
        return 0
    
    verbose = '--verbose' in sys.argv
    
    passed = 0
    failed = 0
    
    print(f"Running {len(test_files)} end-to-end tests...")
    print()
    
    for test_file in sorted(test_files):
        test_name = os.path.basename(test_file)
        print(f"Running {test_name}...")
        
        success = run_filecheck(test_file, verbose)
        if success:
            print(f"PASS: {test_name}")
            passed += 1
        else:
            print(f"FAIL: {test_name}")
            failed += 1
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("Some tests failed!")
        return 1
    else:
        print("All tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())