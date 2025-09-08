"""Integration test for documentation file parsing and metadata extraction."""
import tempfile
from pathlib import Path
import pytest


class TestDocumentationParsing:
    """Test documentation file parsing and metadata extraction."""

    def test_parse_markdown_file_basic_structure(self):
        """Test parsing of basic markdown file structure."""
        markdown_content = """# Main Title

## Section 1
Content for section 1.

### Subsection 1.1
More detailed content.

## Section 2  
Content for section 2.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(markdown_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            # Import here to test the actual parsing functionality once implemented
            from doc_validator.services.doc_parser import DocumentationParser
            
            parser = DocumentationParser()
            parsed_doc = parser.parse_file(temp_path)
            
            # Should extract basic metadata
            assert parsed_doc is not None
            assert parsed_doc.path == temp_path
            assert parsed_doc.name is not None
            assert len(parsed_doc.name) > 0
            
        except ImportError:
            # Parser not implemented yet - test should fail in TDD
            pytest.fail("DocumentationParser service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_extract_file_metadata(self):
        """Test extraction of file metadata (size, modification time, etc.)."""
        test_content = """# Test Document
This is a test document for metadata extraction.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            from doc_validator.services.doc_parser import DocumentationParser
            
            parser = DocumentationParser()
            parsed_doc = parser.parse_file(temp_path)
            
            # Should extract file metadata
            assert parsed_doc.size_bytes > 0
            assert parsed_doc.version is not None  # Could be hash or timestamp
            assert parsed_doc.validation_status is not None
            
        except ImportError:
            pytest.fail("DocumentationParser service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_parse_transrapport_md_structure(self):
        """Test parsing of TransRapport-specific markdown structure."""
        # Simulate structure similar to TRANSRAPPORT.md
        transrapport_content = """TransRapport (Ubuntu) — Architektur‑Blueprint & Inkrementplan (LD‑3.4)

0. Zielbild

TransRapport ist eine lokale, offlinefähige Marker‑Engine‑Anwendung.

1. Architekturübersicht
1.1 Ebenen und Rollen

ATO (Atomic Marker): Regex‑basierte Signale auf Token/Surface‑Ebene.
SEM (Semantic Marker): kombiniert ≥2 distinkte ATO in Fenstern.
CLU (Cluster Marker): aggregiert thematisch verwandte SEM über X‑of‑Y‑Fenster.
MEMA (Meta‑Marker): übergreifende Muster aus mehreren CLUs.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(transrapport_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            from doc_validator.services.doc_parser import DocumentationParser
            
            parser = DocumentationParser()
            parsed_doc = parser.parse_file(temp_path)
            
            # Should recognize TransRapport-specific content
            assert parsed_doc is not None
            assert "TRANSRAPPORT" in parsed_doc.name.upper() or parsed_doc.name == "transrapport"
            
            # Should identify architectural components mentioned
            # (Implementation will determine exact structure)
            
        except ImportError:
            pytest.fail("DocumentationParser service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_parse_architecture_md_structure(self):
        """Test parsing of ARCHITECTURE.md structure."""
        architecture_content = """# TransRapport (Ubuntu, LD‑3.4) · ARCHITECTURE.md

## 0. Zweck & Geltungsbereich

TransRapport ist eine **lokale, offlinefähige** Anwendung zur Analyse.

## 3. Komponenten

1. **CLI‑Fassade (`me`)**: Subcommands für Laden/Validieren/Jobs/Run/View/Export/Reset.
2. **Loader**: liest YAML‑Marker von Disk.
3. **Validator**: Regeln erzwingen.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(architecture_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            from doc_validator.services.doc_parser import DocumentationParser
            
            parser = DocumentationParser()
            parsed_doc = parser.parse_file(temp_path)
            
            # Should recognize Architecture document
            assert parsed_doc is not None
            assert "ARCHITECTURE" in parsed_doc.name.upper() or parsed_doc.name == "architecture"
            
        except ImportError:
            pytest.fail("DocumentationParser service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_handle_invalid_markdown_gracefully(self):
        """Test that parser handles invalid or malformed markdown gracefully."""
        invalid_content = """# Incomplete header
## Missing content

[Broken link](
**Unclosed bold formatting
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(invalid_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            from doc_validator.services.doc_parser import DocumentationParser
            
            parser = DocumentationParser()
            # Should not crash on malformed markdown
            parsed_doc = parser.parse_file(temp_path)
            
            # Should still create a document object, even if parsing had issues
            assert parsed_doc is not None
            assert parsed_doc.path == temp_path
            
        except ImportError:
            pytest.fail("DocumentationParser service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_parse_empty_file(self):
        """Test parsing of empty or whitespace-only files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write("   \n\n  \t  \n")  # Only whitespace
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            from doc_validator.services.doc_parser import DocumentationParser
            
            parser = DocumentationParser()
            parsed_doc = parser.parse_file(temp_path)
            
            # Should handle empty files gracefully
            assert parsed_doc is not None
            assert parsed_doc.path == temp_path
            assert parsed_doc.size_bytes >= 0
            
        except ImportError:
            pytest.fail("DocumentationParser service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)