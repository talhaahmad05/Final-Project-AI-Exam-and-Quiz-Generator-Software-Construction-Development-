"""
filename: run_tests.py
module: Test Runner
author: Talha Ahmad
date: 2026-05-12
Sprint: 5 - Testing & Deployment
"""

import unittest
import sys
import os
import time

def run_all_tests():
    """Discovers and runs all tests in the tests/ directory"""
    print("=" * 60)
    print("  QuizAI Platform -- Automated Test Suite")
    print("  Author: Talha Ahmad | FA-24 BSSE 009")
    print("=" * 60)
    print()

    # Ensure the PARENT of QuizPlatform is in the path so 'QuizPlatform' is importable
    project_root = os.path.dirname(os.path.abspath(__file__))
    parent_root = os.path.dirname(project_root)
    if parent_root not in sys.path:
        sys.path.insert(0, parent_root)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=os.path.join(project_root, 'tests'),
        pattern='test_*.py'
    )

    # Count total tests
    total_tests = suite.countTestCases()
    print(f"  Discovered: {total_tests} test cases")
    print("-" * 60)
    print()

    # Run tests
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    # Summary
    passed = total_tests - len(result.failures) - len(result.errors)
    failed = len(result.failures)
    errors = len(result.errors)

    print()
    print("=" * 60)
    print("  TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"  Tests Run  : {total_tests}")
    print(f"  Passed     : {passed}")
    print(f"  Failed     : {failed}")
    print(f"  Errors     : {errors}")
    print(f"  Time       : {elapsed:.2f}s")
    print(f"  Coverage   : {(passed / total_tests * 100) if total_tests > 0 else 0:.1f}% pass rate")
    print("=" * 60)

    if result.wasSuccessful():
        print("  [PASS] ALL TESTS PASSED!")
    else:
        print("  [FAIL] SOME TESTS FAILED!")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
