#!/usr/bin/env python3
"""
Type Check Hook
Catches type errors and linting issues in code before execution
Similar to TypeScript linter shown in the screenshot
"""

import sys
import subprocess
import os
import json
from pathlib import Path

def check_python_file(file_path):
    """Check Python file for type errors using mypy and flake8"""
    errors = []
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return errors
            
        # Run mypy for type checking
        try:
            result = subprocess.run(
                ["python", "-m", "mypy", file_path, "--no-error-summary", "--show-column-numbers"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        errors.append({
                            'type': 'type',
                            'message': line,
                            'severity': 'error'
                        })
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass  # mypy not installed or failed
            
        # Run flake8 for style and syntax checking
        try:
            result = subprocess.run(
                ["python", "-m", "flake8", file_path, "--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        errors.append({
                            'type': 'lint',
                            'message': line,
                            'severity': 'warning'
                        })
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass  # flake8 not installed or failed
            
    except Exception as e:
        errors.append({
            'type': 'system',
            'message': f"Error checking Python file: {e}",
            'severity': 'error'
        })
    
    return errors

def check_dart_file(file_path):
    """Check Dart/Flutter file for errors using dart analyze"""
    errors = []
    
    try:
        if not os.path.exists(file_path):
            return errors
            
        # Check if we're in a Flutter project
        flutter_project = False
        current_dir = Path(file_path).parent
        while current_dir != current_dir.parent:
            if (current_dir / 'pubspec.yaml').exists():
                flutter_project = True
                break
            current_dir = current_dir.parent
        
        if flutter_project:
            # Change to Flutter project directory
            project_root = current_dir
            relative_path = Path(file_path).relative_to(project_root)
            
            # Run flutter analyze or dart analyze
            try:
                result = subprocess.run(
                    ["flutter", "analyze", str(relative_path), "--no-preamble"],
                    cwd=str(project_root),
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if 'error' in line.lower() or 'warning' in line.lower():
                            errors.append({
                                'type': 'dart',
                                'message': line,
                                'severity': 'error' if 'error' in line.lower() else 'warning'
                            })
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                # Try dart analyze as fallback
                try:
                    result = subprocess.run(
                        ["dart", "analyze", file_path],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.stdout:
                        for line in result.stdout.strip().split('\n'):
                            if 'error' in line.lower() or 'warning' in line.lower():
                                errors.append({
                                    'type': 'dart',
                                    'message': line,
                                    'severity': 'error' if 'error' in line.lower() else 'warning'
                                })
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    pass  # Neither flutter nor dart available
                    
    except Exception as e:
        errors.append({
            'type': 'system',
            'message': f"Error checking Dart file: {e}",
            'severity': 'error'
        })
    
    return errors

def format_errors(errors, file_path):
    """Format errors similar to the TypeScript linter screenshot"""
    if not errors:
        return
    
    print(f"\n🔍 Checking: {file_path}")
    print(f"⚠️  {len(errors)} linter errors")
    print()
    
    for error in errors:
        severity_icon = "❌" if error['severity'] == 'error' else "⚠️"
        print(f"{severity_icon} {error['message']}")
    
    print()
    if len(errors) > 0:
        print(f"🔧 {len([e for e in errors if e['severity'] == 'error'])} errors, {len([e for e in errors if e['severity'] == 'warning'])} warnings")

def main():
    """Main type checking function"""
    # Get file path from environment variables that Claude Code sets
    file_path = None
    
    # Claude Code sets these environment variables for PostToolUse hooks
    file_path = (
        os.environ.get('TOOL_USE_FILE_PATH') or  # File path from tool use
        os.environ.get('CLAUDE_FILE_PATH') or    # Fallback
        (sys.argv[1] if len(sys.argv) > 1 else None)  # Command line arg
    )
    
    if not file_path:
        # Skip silently if no file to check
        return
    
    # Determine file type and run appropriate checker
    file_ext = Path(file_path).suffix.lower()
    errors = []
    
    if file_ext == '.py':
        errors = check_python_file(file_path)
    elif file_ext in ['.dart']:
        errors = check_dart_file(file_path)
    else:
        # Skip type checking for other file types
        return
    
    # Format and display errors
    format_errors(errors, file_path)

if __name__ == "__main__":
    main()