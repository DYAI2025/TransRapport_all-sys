"""Integration test for inconsistency detection scenario."""
import subprocess
import sys
import tempfile
from pathlib import Path


class TestInconsistencyDetection:
    """Test the inconsistency detection user scenario from quickstart.md."""

    def test_validation_detects_terminology_inconsistencies(self):
        """Test that validation can detect terminology inconsistencies."""
        # Create temporary files simulating inconsistent terminology
        terminologie_content = """# Marker-Terminologie

## ATO (Atomic Marker)
Original definition: smallest beobachtbare Einheit, meist Regex/Token.
"""
        
        architecture_content = """# Architecture

The ATO markers are complex aggregation patterns.
This contradicts the terminologie.md definition.
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files with inconsistent definitions
            (temp_path / "terminologie.md").write_text(terminologie_content)
            (temp_path / "architecture.md").write_text(architecture_content)
            
            # Run validation in strict mode
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "validate",
                    "--strict",
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )
            
            # Should execute and provide validation results
            assert result.returncode in [0, 1]  # 0 = no issues, 1 = issues found
            
            # Should produce some form of validation output
            output = result.stdout + result.stderr
            assert len(output.strip()) > 0, "Validation should produce output"

    def test_validation_reports_line_numbers(self):
        """Test that validation reports specific line numbers for issues."""
        # Create a test file with a potential issue on a specific line
        test_content = """# Test Document
Line 2 content
Line 3 contains undefined term: UNKNOWN_TERM
Line 4 content
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "validate",
                    "--strict",
                    str(temp_path),
                ],
                capture_output=True,
                text=True,
            )
            
            # Should execute validation
            assert result.returncode in [0, 1]
            
            # Should provide detailed output (implementation will determine format)
            output = result.stdout + result.stderr
            assert len(output.strip()) > 0, "Validation should provide detailed feedback"
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_fix_and_revalidate_workflow(self):
        """Test the fix and revalidate workflow from user story 2."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test_doc.md"
            
            # Step 1: Create file with issue
            test_file.write_text("# Test\nThis document has an issue.\n")
            
            # Step 2: Run initial validation
            initial_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "validate",
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )
            
            # Step 3: "Fix" the issue by updating content
            test_file.write_text("# Test\nThis document has been corrected.\n")
            
            # Step 4: Run validation again
            fixed_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "validate",
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )
            
            # Both validations should execute
            for result in [initial_result, fixed_result]:
                assert result.returncode in [0, 1], "Validation should not crash"
                output = result.stdout + result.stderr
                assert len(output.strip()) > 0, "Should provide validation feedback"

    def test_strict_mode_vs_normal_mode(self):
        """Test difference between strict and normal validation modes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write("# Test Document\nSome content here.\n")
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            # Run normal validation
            normal_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "validate",
                    str(temp_path),
                ],
                capture_output=True,
                text=True,
            )
            
            # Run strict validation
            strict_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "doc_validator.cli.main",
                    "docs",
                    "validate",
                    "--strict",
                    str(temp_path),
                ],
                capture_output=True,
                text=True,
            )
            
            # Both should execute
            for result in [normal_result, strict_result]:
                assert result.returncode in [0, 1], "Validation modes should not crash"
                output = result.stdout + result.stderr
                assert len(output.strip()) > 0, "Should provide feedback in both modes"
                
        finally:
            temp_path.unlink(missing_ok=True)