"""Integration test for terminology extraction from terminologie.md."""
import tempfile
from pathlib import Path
import pytest


class TestTerminologyParsing:
    """Test terminology extraction from terminologie.md."""

    def test_extract_marker_level_terminology(self):
        """Test extraction of marker level terminology (ATO, SEM, CLU, MEMA)."""
        terminologie_content = """# Marker-Terminologie · Quickref (LD-3.4)

## 1. Ebenen (Bottom-up)
- **ATO_ (Atomic Marker)** · kleinste beobachtbare Einheit, meist Regex/Token.  
  Struktur: `pattern` + `examples (≥5)`  
  Beispiel: ATO_EXAMPLE_SIGNAL ("ja, aber").  
- **SEM_ (Semantic Marker)** · Kombination **≥2 distinkter ATO** in einem Fenster.  
  Struktur: `composed_of: [ATO_…]` + Fensterregel.  
- **CLU_ (Cluster Marker)** · Aggregation thematisch verwandter SEM_ über X-of-Y-Fenster.  
  Struktur: `composed_of: [SEM_…]`, `activation.rule`, optional `scoring`.  
- **MEMA_ (Meta Marker)** · Muster über mehrere CLUs; Regel-Aggregation.  
  Struktur: `composed_of: [CLU_…]` **oder** `detect_class`, + `activation`/`scoring`.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(terminologie_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            from doc_validator.services.terminology_extractor import TerminologyExtractor
            
            extractor = TerminologyExtractor()
            terms = extractor.extract_from_file(temp_path)
            
            # Should extract the four main marker levels
            term_names = [term.term for term in terms]
            assert "ATO" in term_names or "ATO_" in term_names
            assert "SEM" in term_names or "SEM_" in term_names  
            assert "CLU" in term_names or "CLU_" in term_names
            assert "MEMA" in term_names or "MEMA_" in term_names
            
            # Each term should have a definition
            for term in terms:
                assert term.definition is not None
                assert len(term.definition.strip()) > 0
                
        except ImportError:
            pytest.fail("TerminologyExtractor service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_extract_term_definitions_with_aliases(self):
        """Test extraction of terms with their definitions and aliases."""
        terminologie_content = """# Terminologie

## ATO (Atomic Marker)
**Definition**: kleinste beobachtbare Einheit, meist Regex/Token.
**Aliases**: Atomic Marker, ATO_

## SEM (Semantic Marker) 
**Definition**: Kombination ≥2 distinkter ATO in einem Fenster.
**Also known as**: Semantic, SEM_, semantic marker.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(terminologie_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            from doc_validator.services.terminology_extractor import TerminologyExtractor
            
            extractor = TerminologyExtractor()
            terms = extractor.extract_from_file(temp_path)
            
            # Should extract terms with their full definitions
            assert len(terms) >= 2
            
            for term in terms:
                assert term.term is not None
                assert term.definition is not None
                assert len(term.definition.strip()) > 0
                # Aliases may or may not be implemented initially
                assert hasattr(term, 'aliases')
                
        except ImportError:
            pytest.fail("TerminologyExtractor service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_extract_cli_command_terminology(self):
        """Test extraction of CLI command terminology."""
        terminologie_content = """# Terminologie

## CLI Commands

### me markers load
Lädt YAML‑Marker von Disk, prüft Präfixe, Checksums, Schema‑Version.

### me markers validate
Regeln erzwingen: `examples ≥ 5`, exakt **ein** Strukturblock.

### me run scan
Konfigurierter Lauf ATO→SEM→CLU→MEMA, idempotent pro `conv`.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(terminologie_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            from doc_validator.services.terminology_extractor import TerminologyExtractor
            
            extractor = TerminologyExtractor()
            terms = extractor.extract_from_file(temp_path)
            
            # Should extract CLI command terms
            cli_terms = [term for term in terms if 'me ' in term.term.lower()]
            assert len(cli_terms) > 0, "Should extract CLI command terminology"
            
            for term in cli_terms:
                assert term.category is not None  # Should categorize as CLI command
                assert 'cli' in term.category.lower() or 'command' in term.category.lower()
                
        except ImportError:
            pytest.fail("TerminologyExtractor service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_generate_usage_patterns_for_terms(self):
        """Test generation of regex patterns for finding term usage."""
        terminologie_content = """# Terminologie

## ATO
Atomic Marker definition.

## LD-3.4
LEAN.DEEP version 3.4 specification.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(terminologie_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            from doc_validator.services.terminology_extractor import TerminologyExtractor
            
            extractor = TerminologyExtractor()
            terms = extractor.extract_from_file(temp_path)
            
            # Should generate usage patterns for finding terms in text
            for term in terms:
                assert term.usage_pattern is not None
                assert len(term.usage_pattern) > 0
                # Pattern should include the term itself
                assert term.term.lower() in term.usage_pattern.lower()
                
        except ImportError:
            pytest.fail("TerminologyExtractor service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_handle_complex_formatting_in_definitions(self):
        """Test handling of complex markdown formatting in definitions."""
        complex_content = """# Terminologie

## **ATO** (Atomic Marker)
Definition with **bold**, *italic*, `code`, and [links](example.md).

> Blockquote explanation.

- List item 1
- List item 2

### Subsection under ATO
More details here.

## SEM_COMPLEX
Definition with:
1. Numbered list
2. `inline code`
3. **emphasis**

```
Code block example
```
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(complex_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            from doc_validator.services.terminology_extractor import TerminologyExtractor
            
            extractor = TerminologyExtractor()
            terms = extractor.extract_from_file(temp_path)
            
            # Should handle complex formatting gracefully
            assert len(terms) >= 2
            
            for term in terms:
                # Should extract clean term names despite formatting
                assert not any(char in term.term for char in ['*', '`', '[', ']'])
                # Definitions may retain some formatting
                assert term.definition is not None
                assert len(term.definition.strip()) > 0
                
        except ImportError:
            pytest.fail("TerminologyExtractor service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_extract_from_empty_terminologie_file(self):
        """Test extraction from empty or invalid terminologie file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write("# Empty Terminologie\n\nNo terms defined.\n")
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            from doc_validator.services.terminology_extractor import TerminologyExtractor
            
            extractor = TerminologyExtractor()
            terms = extractor.extract_from_file(temp_path)
            
            # Should handle empty file gracefully
            assert isinstance(terms, list)
            # May be empty list or contain minimal extracted info
            
        except ImportError:
            pytest.fail("TerminologyExtractor service not implemented yet")
        finally:
            temp_path.unlink(missing_ok=True)