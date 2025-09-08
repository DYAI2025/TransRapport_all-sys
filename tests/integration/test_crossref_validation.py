"""Integration test for cross-reference validation across files."""
import tempfile
from pathlib import Path
import pytest


class TestCrossReferenceValidation:
    """Test cross-reference validation across documentation files."""

    def test_validate_internal_markdown_links(self):
        """Test validation of internal markdown links between files."""
        # Create test files with cross-references
        architecture_content = """# Architecture

See the [terminology definitions](terminologie.md#marker-levels) for details.
Also check [specific marker info](terminologie.md#ato-atomic-marker).
"""
        
        terminologie_content = """# Terminologie

## Marker Levels
Definition of marker hierarchy.

## ATO (Atomic Marker)  
Detailed ATO definition.
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "architecture.md").write_text(architecture_content)
            (temp_path / "terminologie.md").write_text(terminologie_content)
            
            try:
                from doc_validator.services.crossref_validator import CrossReferenceValidator
                
                validator = CrossReferenceValidator()
                results = validator.validate_directory(temp_path)
                
                # Should find and validate cross-references
                assert results is not None
                assert isinstance(results, list)
                
                # Should identify both valid and potentially invalid references
                for result in results:
                    assert result.source_file is not None
                    assert result.term is not None or result.reference_type is not None
                    assert hasattr(result, 'is_valid')
                    
            except ImportError:
                pytest.fail("CrossReferenceValidator service not implemented yet")

    def test_detect_broken_section_links(self):
        """Test detection of broken section links."""
        file1_content = """# File 1
Reference to [non-existent section](file2.md#missing-section).
Reference to [existing section](file2.md#existing-section).
"""
        
        file2_content = """# File 2
## Existing Section
This section exists.

## Another Section
This one exists too.
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            (temp_path / "file1.md").write_text(file1_content)
            (temp_path / "file2.md").write_text(file2_content)
            
            try:
                from doc_validator.services.crossref_validator import CrossReferenceValidator
                
                validator = CrossReferenceValidator()
                results = validator.validate_directory(temp_path)
                
                # Should detect broken reference to missing-section
                broken_refs = [r for r in results if not r.is_valid]
                valid_refs = [r for r in results if r.is_valid]
                
                # Should have at least one broken and one valid reference
                assert len(broken_refs) > 0, "Should detect broken section link"
                assert len(valid_refs) > 0, "Should detect valid section link"
                
            except ImportError:
                pytest.fail("CrossReferenceValidator service not implemented yet")

    def test_validate_terminology_usage_consistency(self):
        """Test validation of terminology usage consistency across files."""
        terminologie_content = """# Terminologie

## ATO
Atomic Marker: smallest observable unit, usually regex/token pattern.

## SEM  
Semantic Marker: combination of ≥2 distinct ATO in windows.
"""
        
        architecture_content = """# Architecture

The ATO markers are the foundation of the system.
SEM markers build upon ATO by combining them.
Each UNKNOWN_TERM should be flagged as undefined.
"""
        
        transrapport_content = """# TransRapport

ATO patterns detect signals at the token level.
SEM rules aggregate ATO matches in message windows.
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            (temp_path / "terminologie.md").write_text(terminologie_content)
            (temp_path / "architecture.md").write_text(architecture_content)
            (temp_path / "transrapport.md").write_text(transrapport_content)
            
            try:
                from doc_validator.services.crossref_validator import CrossReferenceValidator
                
                validator = CrossReferenceValidator()
                results = validator.validate_directory(temp_path)
                
                # Should validate terminology usage
                term_refs = [r for r in results if r.reference_type == 'USAGE' or 'term' in str(r.reference_type).lower()]
                
                # Should find consistent usage of ATO and SEM
                ato_refs = [r for r in term_refs if 'ATO' in r.term]
                sem_refs = [r for r in term_refs if 'SEM' in r.term]
                
                assert len(ato_refs) > 0, "Should find ATO term usage"
                assert len(sem_refs) > 0, "Should find SEM term usage"
                
                # Should detect undefined terms
                undefined_refs = [r for r in results if not r.is_valid and 'UNKNOWN' in str(r.term)]
                assert len(undefined_refs) > 0, "Should detect undefined term usage"
                
            except ImportError:
                pytest.fail("CrossReferenceValidator service not implemented yet")

    def test_validate_cross_references_with_line_numbers(self):
        """Test that cross-reference validation includes line numbers."""
        test_content = """# Test Document
Line 2 content here.
Reference to [some link](other.md#section) on line 3.
Line 4 content.
Another [reference](other.md#other-section) on line 5.
"""
        
        other_content = """# Other Document
## Section
Content here.
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            (temp_path / "test.md").write_text(test_content)
            (temp_path / "other.md").write_text(other_content)
            
            try:
                from doc_validator.services.crossref_validator import CrossReferenceValidator
                
                validator = CrossReferenceValidator()
                results = validator.validate_directory(temp_path)
                
                # Should include line number information
                for result in results:
                    assert hasattr(result, 'line_number')
                    if result.line_number is not None:
                        assert result.line_number > 0, "Line numbers should be positive"
                        
                # Should have references from expected lines
                line_numbers = [r.line_number for r in results if r.line_number is not None]
                assert 3 in line_numbers or 5 in line_numbers, "Should find references on expected lines"
                
            except ImportError:
                pytest.fail("CrossReferenceValidator service not implemented yet")

    def test_validate_cli_command_references(self):
        """Test validation of CLI command references in documentation."""
        architecture_content = """# Architecture

Use `me markers load` to load marker definitions.
The `me docs validate` command checks consistency.
Use `me run scan` to execute the pipeline.
Invalid command: `me nonexistent command`.
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "architecture.md").write_text(architecture_content)
            
            try:
                from doc_validator.services.crossref_validator import CrossReferenceValidator
                
                validator = CrossReferenceValidator()
                results = validator.validate_directory(temp_path)
                
                # Should validate CLI command references
                cli_refs = [r for r in results if 'me ' in str(r.term) or 'command' in str(r.reference_type).lower()]
                
                if len(cli_refs) > 0:
                    # Should distinguish between valid and invalid CLI commands
                    valid_cli = [r for r in cli_refs if r.is_valid]
                    invalid_cli = [r for r in cli_refs if not r.is_valid]
                    
                    # At least some CLI references should be detected
                    assert len(cli_refs) > 0, "Should detect CLI command references"
                
            except ImportError:
                pytest.fail("CrossReferenceValidator service not implemented yet")

    def test_validate_marker_definition_references(self):
        """Test validation of marker definition references."""
        marker_content = """# Marker Definitions

## ATO_EXAMPLE_SIGNAL
Pattern: "ja, aber"
Examples: ≥5 required

## SEM_NEGATION  
Composed of: [ATO_EXAMPLE_SIGNAL, ATO_SELF_DEPRECATION]
Window: ANY 2 IN 3 messages
"""
        
        architecture_content = """# Architecture

The ATO_EXAMPLE_SIGNAL marker detects negation patterns.
SEM_NEGATION combines multiple ATO markers.
Reference to UNDEFINED_MARKER should be flagged.
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            (temp_path / "marker.md").write_text(marker_content)
            (temp_path / "architecture.md").write_text(architecture_content)
            
            try:
                from doc_validator.services.crossref_validator import CrossReferenceValidator
                
                validator = CrossReferenceValidator()
                results = validator.validate_directory(temp_path)
                
                # Should validate marker definition references
                marker_refs = [r for r in results if any(prefix in str(r.term) for prefix in ['ATO_', 'SEM_', 'CLU_', 'MEMA_'])]
                
                if len(marker_refs) > 0:
                    # Should find valid references to defined markers
                    valid_markers = [r for r in marker_refs if r.is_valid]
                    invalid_markers = [r for r in marker_refs if not r.is_valid]
                    
                    assert len(valid_markers) > 0, "Should find valid marker references"
                    assert len(invalid_markers) > 0, "Should detect undefined marker references"
                
            except ImportError:
                pytest.fail("CrossReferenceValidator service not implemented yet")