"""Implementation of 'me docs status' CLI command."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import click

from ..services.crossref_validator import CrossReferenceValidator
from ..services.doc_parser import DocumentationParser
from ..services.terminology_extractor import TerminologyExtractor
from .utils import resolve_docs_root


@click.command()
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), 
              default='text', help='Output format')
def status(output_format: str) -> None:
    """Get documentation status."""
    current_dir = resolve_docs_root(Path.cwd())
    
    # Parse documentation files
    doc_parser = DocumentationParser()
    doc_files = doc_parser.parse_directory(current_dir)
    
    # Get core TransRapport files
    core_files = doc_parser.identify_transrapport_files(doc_files)
    
    # Extract terminology statistics
    term_stats = _get_terminology_statistics(current_dir)
    
    # Get cross-reference statistics
    crossref_stats = _get_crossref_statistics(current_dir)
    
    # Determine overall status
    overall_status = _determine_overall_status(doc_files)
    
    # Prepare results
    results = {
        "files": _format_file_status(doc_files, core_files),
        "last_validation": datetime.now().isoformat(),
        "overall_status": overall_status,
        "statistics": {
            "total_terms": term_stats["total_terms"],
            "total_references": crossref_stats["total_references"],
            "broken_references": crossref_stats["broken_references"]
        }
    }
    
    if output_format == 'json':
        click.echo(json.dumps(results, indent=2))
    else:
        _format_status_text_output(results, core_files)


def _get_terminology_statistics(directory: Path) -> Dict[str, int]:
    """Get terminology statistics from directory."""
    extractor = TerminologyExtractor()
    
    total_terms = 0
    
    # Look for terminologie.md specifically
    for md_file in directory.glob('**/*terminologie*.md'):
        terms = extractor.extract_from_file(md_file)
        total_terms += len(terms)
    
    # If no terminologie.md found, count terms from all files
    if total_terms == 0:
        for md_file in directory.glob('**/*.md'):
            terms = extractor.extract_from_file(md_file)
            total_terms += len(terms)
    
    return {"total_terms": total_terms}


def _get_crossref_statistics(directory: Path) -> Dict[str, int]:
    """Get cross-reference statistics from directory."""
    try:
        validator = CrossReferenceValidator()
        cross_refs = validator.validate_directory(directory)
        
        total_references = len(cross_refs)
        broken_references = sum(1 for ref in cross_refs if not ref.is_valid)
        
        return {
            "total_references": total_references,
            "broken_references": broken_references
        }
    except Exception:
        return {
            "total_references": 0,
            "broken_references": 0
        }


def _determine_overall_status(doc_files: List) -> str:
    """Determine overall documentation status."""
    if not doc_files:
        return "not_validated"
    
    # Check validation status of files
    invalid_files = [f for f in doc_files if f.validation_status.value == "invalid"]
    not_validated_files = [f for f in doc_files if f.validation_status.value == "not_validated"]
    
    if invalid_files:
        return "invalid"
    elif not_validated_files:
        return "not_validated"
    else:
        return "valid"


def _format_file_status(doc_files: List, core_files: Dict) -> List[Dict]:
    """Format file status information."""
    file_status = []
    
    # Add core files first
    for file_type, doc_file in core_files.items():
        if doc_file:
            file_status.append({
                "path": str(doc_file.path),
                "name": f"{file_type.upper()}.md",
                "status": doc_file.validation_status.value,
                "last_modified": datetime.fromtimestamp(doc_file.path.stat().st_mtime).isoformat(),
                "last_validated": doc_file.last_validated.isoformat() if doc_file.last_validated else None,
                "issue_count": {"errors": 0, "warnings": 0}  # Simplified for now
            })
    
    # Add other files
    core_paths = {str(f.path) for f in core_files.values() if f}
    for doc_file in doc_files:
        if str(doc_file.path) not in core_paths:
            file_status.append({
                "path": str(doc_file.path),
                "name": doc_file.path.name,
                "status": doc_file.validation_status.value,
                "last_modified": datetime.fromtimestamp(doc_file.path.stat().st_mtime).isoformat(),
                "last_validated": doc_file.last_validated.isoformat() if doc_file.last_validated else None,
                "issue_count": {"errors": 0, "warnings": 0}
            })
    
    return file_status


def _format_status_text_output(results: Dict, core_files: Dict) -> None:
    """Format status results as human-readable text."""
    files = results.get('files', [])
    statistics = results.get('statistics', {})
    overall_status = results.get('overall_status', 'unknown')
    
    click.echo("Documentation Status Report")
    click.echo()
    
    if not files:
        click.echo("No documentation files found")
        return
    
    # Display core files status
    click.echo("Files:")
    
    core_file_names = {'transrapport', 'architecture', 'terminologie', 'marker'}
    
    for file_info in files:
        file_name = file_info['name']
        status = file_info['status']
        last_validated = file_info['last_validated']
        
        status_symbol = {
            'valid': '✓',
            'invalid': '✗',
            'not_validated': '?'
        }.get(status, '?')
        
        # Format validation time
        if last_validated:
            validated_time = datetime.fromisoformat(last_validated).strftime('%Y-%m-%d %H:%M:%S')
            time_info = f"Last validated: {validated_time}"
        else:
            time_info = "Not validated"
        
        click.echo(f"{status_symbol} {file_name:<20} {time_info}")
    
    # Display statistics
    click.echo()
    click.echo("Statistics:")
    click.echo(f"- Total terms defined: {statistics.get('total_terms', 0)}")
    click.echo(f"- Total references: {statistics.get('total_references', 0)}")
    click.echo(f"- Broken references: {statistics.get('broken_references', 0)}")
    click.echo(f"- Last full validation: {datetime.fromisoformat(results['last_validation']).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display overall status
    click.echo()
    status_text = {
        'valid': 'VALID',
        'invalid': 'INVALID',
        'not_validated': 'NOT VALIDATED'
    }.get(overall_status, 'UNKNOWN')
    
    click.echo(f"Overall Status: {status_text}")