"""Implementation of 'me docs cross-ref' CLI command."""
import click
import json
from pathlib import Path
from typing import List, Optional

from ..models.cross_reference import CrossReference
from ..services.crossref_validator import CrossReferenceValidator
from .utils import resolve_docs_root


@click.command(name="cross-ref")
@click.option("--term", help="Specific term to check references for")
@click.option(
    "--file",
    "file_path",
    type=click.Path(exists=True, path_type=Path),
    help="Specific file to check references in",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
def cross_ref(
    term: Optional[str], file_path: Optional[Path], output_format: str
) -> None:
    """Check cross-references."""
    validator = CrossReferenceValidator()
    
    if file_path:
        # Check references in specific file
        file_refs = validator._validate_file(file_path)
        all_refs = file_refs
    else:
        # Check references in detected documentation root
        docs_root = resolve_docs_root(Path.cwd())
        all_refs = validator.validate_directory(docs_root)
    
    # Filter by term if specified
    if term:
        all_refs = [ref for ref in all_refs if term.lower() in ref.term.lower()]
    
    # Prepare results
    results = _prepare_crossref_results(all_refs, term)
    
    if output_format == 'json':
        click.echo(json.dumps(results, indent=2))
    else:
        _format_crossref_text_output(results, term, file_path)


def _prepare_crossref_results(references: List[CrossReference], term_filter: Optional[str]) -> dict:
    """Prepare cross-reference results for output."""
    # Group references by term
    refs_by_term = {}
    broken_links = []
    
    for ref in references:
        term = ref.term
        if term not in refs_by_term:
            refs_by_term[term] = []
        
        ref_data = {
            "term": ref.term,
            "file": ref.source_file,
            "line": ref.line_number,
            "context": ref.get_context_preview(50),
            "valid": ref.is_valid,
            "reference_type": ref.reference_type.value
        }
        
        refs_by_term[term].append(ref_data)
        
        if not ref.is_valid:
            broken_links.append({
                "file": ref.source_file,
                "line": ref.line_number,
                "link": ref.term,
                "target": ref.term  # Simplified for now
            })
    
    # Convert to list format expected by contract
    references_list = []
    for term, refs in refs_by_term.items():
        references_list.extend(refs)
    
    return {
        "term_count": len(refs_by_term),
        "references": references_list,
        "broken_links": broken_links
    }


def _format_crossref_text_output(
    results: dict, term_filter: Optional[str], file_filter: Optional[Path]
) -> None:
    """Format cross-reference results as human-readable text."""
    references = results.get('references', [])
    broken_links = results.get('broken_links', [])
    term_count = results.get('term_count', 0)
    
    if not references:
        if term_filter:
            click.echo(f"No references found for term: {term_filter}")
        elif file_filter:
            click.echo(f"No cross-references found in: {Path(file_filter).name}")
        else:
            click.echo("No cross-references found in documentation")
        return
    
    click.echo("Cross-Reference Report:")
    click.echo()
    
    if term_filter:
        click.echo(f"References for '{term_filter}':")
        _display_term_references(references, term_filter)
    else:
        # Group by term for display
        refs_by_term = {}
        for ref in references:
            term = ref['term']
            if term not in refs_by_term:
                refs_by_term[term] = []
            refs_by_term[term].append(ref)
        
        click.echo(f"Terms Checked: {term_count}")
        
        for term, term_refs in refs_by_term.items():
            valid_count = sum(1 for r in term_refs if r['valid'])
            total_count = len(term_refs)
            
            if valid_count == total_count:
                click.echo(f"✓ {term}: {total_count} references, all valid")
            else:
                invalid_count = total_count - valid_count
                click.echo(f"✗ {term}: {total_count} references, {invalid_count} broken")
                
                # Show broken references
                for ref in term_refs:
                    if not ref['valid']:
                        file_name = Path(ref['file']).name
                        click.echo(f"  - {file_name}:{ref['line']} → broken reference")
    
    # Display broken links summary
    if broken_links:
        click.echo()
        click.echo("Broken Links:")
        for link in broken_links:
            file_name = Path(link['file']).name
            click.echo(f"- {file_name}:{link['line']} → '{link['link']}' (target not found)")
    
    # Summary
    click.echo()
    total_refs = len(references)
    broken_count = len(broken_links)
    click.echo(f"Summary: {total_refs} references checked, {broken_count} broken")


def _display_term_references(references: List[dict], term: str) -> None:
    """Display references for a specific term."""
    term_refs = [ref for ref in references if ref['term'].lower() == term.lower()]
    
    if not term_refs:
        click.echo("No references found")
        return
    
    for ref in term_refs:
        file_name = Path(ref['file']).name
        status = "✓" if ref['valid'] else "✗"
        type_info = f"({ref['reference_type']})" if ref['reference_type'] != 'usage' else ""
        
        click.echo(f"  {status} {file_name}:{ref['line']} {type_info}")
        
        if ref['context']:
            context = ref['context'][:80] + "..." if len(ref['context']) > 80 else ref['context']
            click.echo(f"    Context: {context}")
        
        if not ref['valid']:
            click.echo(f"    Issue: Reference appears to be broken or undefined")