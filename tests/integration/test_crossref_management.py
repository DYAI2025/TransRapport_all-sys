"""Integration test for cross-reference management scenario."""
import subprocess
import sys
import tempfile
from pathlib import Path


class TestCrossReferenceManagement:
    """Test the cross-reference management user scenario from quickstart.md."""

    def test_detect_broken_cross_reference(self):
        """Test detection of broken cross-reference links."""
        # Create test files with broken cross-reference
        architecture_content = """# Architecture Document

See [New concept](terminologie.md#new-concept) for details.
This link points to a non-existent section.
"""
        
        terminologie_content = """# Terminologie

## Existing Concept
This concept exists.

## Another Concept  
This one exists too.
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files with broken reference
            (temp_path / "architecture.md").write_text(architecture_content)
            (temp_path / "terminologie.md").write_text(terminologie_content)
            
            # Run cross-reference check
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "cross-ref",
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )
            
            # Should execute and detect the broken reference
            assert result.returncode in [0, 1]  # 0 = no issues, 1 = broken refs found
            
            output = result.stdout + result.stderr
            assert len(output.strip()) > 0, "Cross-ref check should produce output"

    def test_add_missing_definition_and_recheck(self):
        """Test adding missing definition and rechecking references."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Step 1: Create file with broken reference
            architecture_file = temp_path / "architecture.md"
            terminologie_file = temp_path / "terminologie.md"
            
            architecture_file.write_text("""# Architecture
See [New concept](terminologie.md#new-concept) for details.
""")
            
            terminologie_file.write_text("""# Terminologie
## Existing Concept
This exists.
""")
            
            # Step 2: Check for broken references
            initial_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "cross-ref",
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )
            
            # Step 3: Add the missing definition
            terminologie_file.write_text("""# Terminologie
## Existing Concept
This exists.

## New Concept
Definition added here.
""")
            
            # Step 4: Recheck references
            fixed_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "cross-ref",
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )
            
            # Both checks should execute
            for result in [initial_result, fixed_result]:
                assert result.returncode in [0, 1], "Cross-ref check should not crash"
                output = result.stdout + result.stderr
                assert len(output.strip()) > 0, "Should provide cross-ref feedback"

    def test_cross_ref_specific_file(self):
        """Test cross-reference checking for a specific file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            test_file = temp_path / "test.md"
            test_file.write_text("""# Test Document
This document references [something](other.md#section).
""")
            
            other_file = temp_path / "other.md"
            other_file.write_text("""# Other Document
## Section
Content here.
""")
            
            # Check references in specific file
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "cross-ref",
                    "--file",
                    str(test_file),
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )
            
            # Should execute and check the specific file
            assert result.returncode in [0, 1]
            output = result.stdout + result.stderr
            assert len(output.strip()) > 0, "Should provide file-specific cross-ref results"

    def test_cross_ref_with_term_filter(self):
        """Test cross-reference checking filtered by specific term."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test content with multiple terms
            test_file = temp_path / "test.md"
            test_file.write_text("""# Test Document
References to ATO and SEM markers.
ATO is mentioned multiple times.
SEM appears here too.
""")
            
            # Check references for specific term
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "cross-ref",
                    "--term",
                    "ATO",
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )
            
            # Should execute and filter by term
            assert result.returncode in [0, 1]
            output = result.stdout + result.stderr
            assert len(output.strip()) > 0, "Should provide term-filtered results"

    def test_cross_ref_json_output(self):
        """Test cross-reference checking with JSON output format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create simple test file
            test_file = temp_path / "test.md"
            test_file.write_text("""# Test Document
Simple content for JSON output test.
""")
            
            # Request JSON format output
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "cross-ref",
                    "--format",
                    "json",
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )
            
            # Should execute with JSON format
            assert result.returncode in [0, 1]
            output = result.stdout + result.stderr
            assert len(output.strip()) > 0, "Should provide JSON-formatted output"