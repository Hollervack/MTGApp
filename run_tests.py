#!/usr/bin/env python3
"""Script to run all tests for the MTG Deck Constructor project

This script runs all unit and integration tests,
generates coverage reports and provides a summary of results.

Usage:
    python run_tests.py [options]
    
Options:
    --verbose, -v: Verbose output
    --coverage, -c: Generate coverage report
    --integration, -i: Integration tests only
    --unit, -u: Unit tests only
    --help, -h: Show this help
"""

import sys
import os
import unittest
import argparse
from io import StringIO

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def discover_tests(test_dir='tests', pattern='test_*.py'):
    """Discover all tests in the specified directory"""
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), test_dir)
    suite = loader.discover(start_dir, pattern=pattern)
    return suite


def run_specific_tests(test_modules):
    """Run specific tests by module"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for module in test_modules:
        try:
            tests = loader.loadTestsFromName(f'tests.{module}')
            suite.addTests(tests)
        except ImportError as e:
            print(f"Error importing {module}: {e}")
    
    return suite


def run_tests_with_coverage(suite, verbose=False):
    """Run tests with coverage report"""
    try:
        import coverage
        
        # Initialize coverage
        cov = coverage.Coverage(source=['src'])
        cov.start()
        
        # Run tests
        runner = unittest.TextTestRunner(
            verbosity=2 if verbose else 1,
            stream=sys.stdout
        )
        result = runner.run(suite)
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("COVERAGE REPORT")
        print("="*50)
        cov.report()
        
        # Generate HTML report if possible
        try:
            cov.html_report(directory='htmlcov')
            print("\nHTML report generated at: htmlcov/index.html")
        except Exception as e:
            print(f"Could not generate HTML report: {e}")
        
        return result
        
    except ImportError:
        print("Warning: coverage is not installed. Running tests without coverage.")
        print("To install: pip install coverage")
        return run_tests_simple(suite, verbose)


def run_tests_simple(suite, verbose=False):
    """Run tests without coverage"""
    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        stream=sys.stdout
    )
    return runner.run(suite)


def print_test_summary(result):
    """Print test results summary"""
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(getattr(result, 'skipped', []))
    passed = total_tests - failures - errors - skipped
    
    print(f"Tests run: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")
    
    if failures > 0:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if errors > 0:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\n')[-2]}")
    
    success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All tests passed!")
    elif success_rate >= 80:
        print("✅ Most tests passed")
    else:
        print("❌ Many tests failed - review code")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Run tests for the MTG Deck Constructor project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Generate coverage report'
    )
    
    parser.add_argument(
        '--integration', '-i',
        action='store_true',
        help='Integration tests only'
    )
    
    parser.add_argument(
        '--unit', '-u',
        action='store_true',
        help='Unit tests only'
    )
    
    parser.add_argument(
        '--module', '-m',
        action='append',
        help='Run specific module (e.g.: test_models)'
    )
    
    args = parser.parse_args()
    
    print("MTG Deck Constructor - Test Runner")
    print("="*40)
    
    # Determine which tests to run
    if args.module:
        print(f"Running specific modules: {', '.join(args.module)}")
        suite = run_specific_tests(args.module)
    elif args.integration:
        print("Running integration tests only...")
        suite = run_specific_tests(['test_integration'])
    elif args.unit:
        print("Running unit tests only...")
        suite = run_specific_tests(['test_models', 'test_services', 'test_controllers'])
    else:
        print("Running all tests...")
        suite = discover_tests()
    
    # Run tests
    if args.coverage:
        result = run_tests_with_coverage(suite, args.verbose)
    else:
        result = run_tests_simple(suite, args.verbose)
    
    # Show summary
    print_test_summary(result)
    
    # Exit code
    if result.failures or result.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()