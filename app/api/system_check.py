"""
FERRARI SYSTEM CHECK - Complete dependency and module verification
"""

from flask import Blueprint, jsonify
import sys
import os

system_check = Blueprint('system_check', __name__)


@system_check.route('/system/check', methods=['GET'])
def complete_system_check():
    """
    Run complete system check - Ferrari inspection!
    Tests EVERYTHING: modules, imports, configurations
    """
    results = {
        'python': check_python(),
        'dependencies': check_dependencies(),
        'modules': check_app_modules(),
        'environment': check_environment(),
        'system_packages': check_system_packages()
    }
    
    # Calculate overall status
    all_critical_ok = (
        results['dependencies']['critical_missing'] == 0 and
        results['modules']['import_errors'] == 0
    )
    
    return jsonify({
        'success': all_critical_ok,
        'status': 'ferrari_ready' if all_critical_ok else 'needs_repair',
        'results': results,
        'summary': generate_summary(results)
    }), 200 if all_critical_ok else 503


def check_python():
    """Check Python environment"""
    return {
        'version': sys.version,
        'executable': sys.executable,
        'platform': sys.platform
    }


def check_dependencies():
    """Check if critical Python packages are installed"""
    critical = [
        'google.generativeai',
        'reportlab',
        'docx',
        'pptx',
        'markdown2',
        'flask',
        'sqlalchemy'
    ]
    
    optional = [
        'pytesseract',
        'PIL',
        'boto3',
        'google.cloud.vision'
    ]
    
    critical_results = {}
    optional_results = {}
    
    for module in critical:
        try:
            __import__(module)
            critical_results[module] = 'installed'
        except ImportError:
            critical_results[module] = 'MISSING'
    
    for module in optional:
        try:
            __import__(module)
            optional_results[module] = 'installed'
        except ImportError:
            optional_results[module] = 'missing'
    
    critical_missing = sum(1 for v in critical_results.values() if v == 'MISSING')
    optional_missing = sum(1 for v in optional_results.values() if v == 'missing')
    
    return {
        'critical': critical_results,
        'optional': optional_results,
        'critical_missing': critical_missing,
        'optional_missing': optional_missing
    }


def check_app_modules():
    """Check if our app modules can be imported"""
    modules_to_test = [
        ('app.funding.document_generator', 'Funding Document Generator'),
        ('app.funding.document_converter', 'Document Converter'),
        ('app.funding.package_manager', 'Package Manager'),
        ('app.ai.real_analysis_engine', 'Real AI Analysis'),
        ('app.ocr.ocr_engine', 'OCR Engine'),
        ('app.expenses.expense_manager', 'Expense Manager'),
        ('app.email_service', 'Email Service')
    ]
    
    results = {}
    errors = []
    
    for module_path, description in modules_to_test:
        try:
            __import__(module_path)
            results[description] = 'OK'
        except Exception as e:
            results[description] = f'FAILED: {str(e)}'
            errors.append({
                'module': module_path,
                'error': str(e)
            })
    
    return {
        'modules': results,
        'import_errors': len(errors),
        'errors': errors
    }


def check_environment():
    """Check environment variables"""
    return {
        'GOOGLE_API_KEY': 'SET' if os.getenv('GOOGLE_API_KEY') else 'MISSING',
        'MAIL_USERNAME': 'SET' if os.getenv('MAIL_USERNAME') else 'MISSING',
        'MAIL_PASSWORD': 'SET' if os.getenv('MAIL_PASSWORD') else 'MISSING',
        'DATABASE_URL': 'SET' if os.getenv('DATABASE_URL') else 'MISSING',
        'AWS_ACCESS_KEY_ID': 'SET' if os.getenv('AWS_ACCESS_KEY_ID') else 'NOT SET (optional)',
        'GOOGLE_APPLICATION_CREDENTIALS': 'SET' if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') else 'NOT SET (optional)'
    }


def check_system_packages():
    """Check system-level packages"""
    import subprocess
    
    packages = {
        'tesseract': 'tesseract --version',
        'poppler': 'pdfinfo -v',
        'imagemagick': 'convert -version'
    }
    
    results = {}
    
    for pkg_name, command in packages.items():
        try:
            result = subprocess.run(
                command.split()[0] + ' --version',
                capture_output=True,
                text=True,
                timeout=2,
                shell=True
            )
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                results[pkg_name] = f'INSTALLED: {version}'
            else:
                results[pkg_name] = 'NOT INSTALLED'
        except:
            results[pkg_name] = 'NOT INSTALLED'
    
    return results


def generate_summary(results):
    """Generate human-readable summary"""
    summary = []
    
    # Critical dependencies
    critical_missing = results['dependencies']['critical_missing']
    if critical_missing > 0:
        summary.append(f'❌ {critical_missing} critical dependencies missing')
    else:
        summary.append('✅ All critical dependencies installed')
    
    # Module imports
    import_errors = results['modules']['import_errors']
    if import_errors > 0:
        summary.append(f'❌ {import_errors} module import errors')
    else:
        summary.append('✅ All app modules import successfully')
    
    # Environment
    env = results['environment']
    if env['GOOGLE_API_KEY'] == 'MISSING':
        summary.append('❌ GOOGLE_API_KEY not set')
    else:
        summary.append('✅ AI configured')
    
    if env['MAIL_USERNAME'] == 'MISSING' or env['MAIL_PASSWORD'] == 'MISSING':
        summary.append('❌ Email not configured')
    else:
        summary.append('✅ Email configured')
    
    return summary
