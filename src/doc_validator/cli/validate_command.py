"""Implementation of 'me docs validate' CLI command."""
import click
import json
from pathlib import Path
from typing import Optional

from ..services.validation_engine import ValidationEngine
from ..services.doc_parser import DocumentationParser
from .utils import resolve_docs_root


@click.command()
@click.option('--strict', is_flag=True, help='Enable strict validation mode')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), 
              default='text', help='Output format')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def validate(strict: bool, output_format: str, files: tuple) -> None:
    """Validate documentation consistency."""
    validation_engine = ValidationEngine()
    
    if files:
        # Validate specific files
        results = _validate_specific_files(validation_engine, files, strict)
    else:
        # Validate all documentation in detected documentation root
        docs_root = resolve_docs_root(Path.cwd())
        results = validation_engine.validate_directory(docs_root, strict=strict)
    
    if output_format == 'json':
        click.echo(json.dumps(results, indent=2))
    else:
        _format_text_output(results)
    
    # Set exit code based on validation results
    if not results.get('success', True):
        exit(1)


def _validate_specific_files(engine: ValidationEngine, files: tuple, strict: bool) -> dict:
    """Validate specific files."""
    doc_parser = DocumentationParser()
    all_issues = []
    
    for file_path in files:
        path = Path(file_path)
        if path.suffix.lower() == '.md':
            try:
                doc_file = doc_parser.parse_file(path)
                file_issues = engine.validate_file(doc_file, strict=strict)
                all_issues.extend(file_issues)
            except Exception as e:
                click.echo(f"Error processing {file_path}: {e}", err=True)
    
    # Calculate summary
    summary = engine._calculate_summary(all_issues)
    success = summary["errors"] == 0 or (not strict and summary["errors"] == 0)
    
    return {
        "success": success,
        "file_count": len(files),
        "issues": [issue.to_dict() for issue in all_issues],
        "summary": summary
    }


def _format_text_output(results: dict) -> None:
    """Format validation results as human-readable text."""
    issues = results.get('issues', [])
    summary = results.get('summary', {})
    file_count = results.get('file_count', 0)
    success = results.get('success', True)
    
    if not issues:
        if file_count > 0:
            click.echo("✓ All documentation files are valid")
            click.echo(f"Files checked: {file_count}")
        else:
            click.echo("No documentation files found to validate")
        return
    
    # Group issues by file
    issues_by_file = {}
    for issue in issues:
        file_path = issue['file']
        if file_path not in issues_by_file:
            issues_by_file[file_path] = []
        issues_by_file[file_path].append(issue)
    
    # Display issues grouped by file
    for file_path, file_issues in issues_by_file.items():
        file_name = Path(file_path).name
        error_count = sum(1 for i in file_issues if i['severity'] == 'error')
        
        if error_count > 0:
            click.echo(f"✗ {file_name}: {len(file_issues)} issues found")
        else:
            click.echo(f"⚠ {file_name}: {len(file_issues)} warnings found")
        
        for issue in file_issues:
            severity_symbol = {
                'error': '✗',
                'warning': '⚠',
                'info': 'ℹ'
            }.get(issue['severity'], '•')
            
            line_info = f" (line {issue['line']})" if issue['line'] else ""
            click.echo(f"  {severity_symbol} {issue['message']}{line_info}")
            
            if issue.get('suggestion'):
                click.echo(f"    Suggestion: {issue['suggestion']}")
    
    # Display summary
    click.echo()
    click.echo("Validation Summary:")
    click.echo(f"- Files checked: {file_count}")
    click.echo(f"- Issues found: {len(issues)} ({summary.get('errors', 0)} errors, {summary.get('warnings', 0)} warnings)")
    
    if success:
        click.echo("- Status: PASS")
    else:
        click.echo("- Status: FAIL")