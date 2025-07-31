#!/usr/bin/env python3
"""Script para ejecutar todos los tests del proyecto MTG Deck Constructor

Este script ejecuta todos los tests unitarios y de integración,
genera reportes de cobertura y proporciona un resumen de resultados.

Uso:
    python run_tests.py [opciones]
    
Opciones:
    --verbose, -v: Salida detallada
    --coverage, -c: Generar reporte de cobertura
    --integration, -i: Solo tests de integración
    --unit, -u: Solo tests unitarios
    --help, -h: Mostrar esta ayuda
"""

import sys
import os
import unittest
import argparse
from io import StringIO

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def discover_tests(test_dir='tests', pattern='test_*.py'):
    """Descubrir todos los tests en el directorio especificado"""
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), test_dir)
    suite = loader.discover(start_dir, pattern=pattern)
    return suite


def run_specific_tests(test_modules):
    """Ejecutar tests específicos por módulo"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for module in test_modules:
        try:
            tests = loader.loadTestsFromName(f'tests.{module}')
            suite.addTests(tests)
        except ImportError as e:
            print(f"Error importando {module}: {e}")
    
    return suite


def run_tests_with_coverage(suite, verbose=False):
    """Ejecutar tests con reporte de cobertura"""
    try:
        import coverage
        
        # Inicializar coverage
        cov = coverage.Coverage(source=['src'])
        cov.start()
        
        # Ejecutar tests
        runner = unittest.TextTestRunner(
            verbosity=2 if verbose else 1,
            stream=sys.stdout
        )
        result = runner.run(suite)
        
        # Detener coverage y generar reporte
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("REPORTE DE COBERTURA")
        print("="*50)
        cov.report()
        
        # Generar reporte HTML si es posible
        try:
            cov.html_report(directory='htmlcov')
            print("\nReporte HTML generado en: htmlcov/index.html")
        except Exception as e:
            print(f"No se pudo generar reporte HTML: {e}")
        
        return result
        
    except ImportError:
        print("Advertencia: coverage no está instalado. Ejecutando tests sin cobertura.")
        print("Para instalar: pip install coverage")
        return run_tests_simple(suite, verbose)


def run_tests_simple(suite, verbose=False):
    """Ejecutar tests sin cobertura"""
    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        stream=sys.stdout
    )
    return runner.run(suite)


def print_test_summary(result):
    """Imprimir resumen de resultados de tests"""
    print("\n" + "="*50)
    print("RESUMEN DE TESTS")
    print("="*50)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(getattr(result, 'skipped', []))
    passed = total_tests - failures - errors - skipped
    
    print(f"Tests ejecutados: {total_tests}")
    print(f"Exitosos: {passed}")
    print(f"Fallidos: {failures}")
    print(f"Errores: {errors}")
    print(f"Omitidos: {skipped}")
    
    if failures > 0:
        print("\nFALLOS:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if errors > 0:
        print("\nERRORES:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\n')[-2]}")
    
    success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"\nTasa de éxito: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 ¡Todos los tests pasaron!")
    elif success_rate >= 80:
        print("✅ La mayoría de tests pasaron")
    else:
        print("❌ Muchos tests fallaron - revisar código")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Ejecutar tests del proyecto MTG Deck Constructor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Salida detallada'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Generar reporte de cobertura'
    )
    
    parser.add_argument(
        '--integration', '-i',
        action='store_true',
        help='Solo tests de integración'
    )
    
    parser.add_argument(
        '--unit', '-u',
        action='store_true',
        help='Solo tests unitarios'
    )
    
    parser.add_argument(
        '--module', '-m',
        action='append',
        help='Ejecutar módulo específico (ej: test_models)'
    )
    
    args = parser.parse_args()
    
    print("MTG Deck Constructor - Test Runner")
    print("="*40)
    
    # Determinar qué tests ejecutar
    if args.module:
        print(f"Ejecutando módulos específicos: {', '.join(args.module)}")
        suite = run_specific_tests(args.module)
    elif args.integration:
        print("Ejecutando solo tests de integración...")
        suite = run_specific_tests(['test_integration'])
    elif args.unit:
        print("Ejecutando solo tests unitarios...")
        suite = run_specific_tests(['test_models', 'test_services', 'test_controllers'])
    else:
        print("Ejecutando todos los tests...")
        suite = discover_tests()
    
    # Ejecutar tests
    if args.coverage:
        result = run_tests_with_coverage(suite, args.verbose)
    else:
        result = run_tests_simple(suite, args.verbose)
    
    # Mostrar resumen
    print_test_summary(result)
    
    # Código de salida
    if result.failures or result.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()