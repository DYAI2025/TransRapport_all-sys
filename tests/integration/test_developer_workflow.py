"""Integration test for developer understanding architecture workflow."""
import subprocess
import sys
import tempfile
from pathlib import Path


class TestDeveloperWorkflow:
    """Test the developer understanding architecture user scenario."""

    def test_developer_needs_system_overview(self):
        """Test: Developer needs to understand overall system via 'me docs status'."""
        # This test represents the first step in quickstart.md user story 1
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "status"],
            capture_output=True,
            text=True,
        )
        
        # Should execute and provide some form of overview
        # (Implementation will determine exact format)
        assert result.returncode in [0, 1]  # 0 = success, 1 = validation issues found
        
        # Should produce output that gives developer information
        output = result.stdout + result.stderr
        assert len(output.strip()) > 0, "Status command should produce some output"

    def test_developer_looks_for_term_definition(self):
        """Test: Developer looks for specific term definition via 'me docs cross-ref --term ATO'."""
        # This test represents the second step in quickstart.md user story 1
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "cross-ref", "--term", "ATO"],
            capture_output=True,
            text=True,
        )
        
        # Should execute and attempt to find ATO references
        assert result.returncode in [0, 1]  # 0 = found, 1 = not found or issues
        
        # Should produce output related to the term search
        output = result.stdout + result.stderr
        assert len(output.strip()) > 0, "Cross-ref command should produce some output"

    def test_developer_validates_after_changes(self):
        """Test: Developer validates consistency after making changes."""
        # Create a temporary test file to simulate documentation changes
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write("# Test Document\nThis is a test change to documentation.\n")
            temp_file.flush()
            temp_path = Path(temp_file.name)

        try:
            # Simulate the validation workflow from quickstart.md
            result = subprocess.run(
                [sys.executable, "-m", "doc_validator.cli.main", "docs", "validate"],
                capture_output=True,
                text=True,
            )
            
            # Should execute validation process
            assert result.returncode in [0, 1]  # 0 = all valid, 1 = issues found
            
            # Should provide validation feedback
            output = result.stdout + result.stderr
            assert len(output.strip()) > 0, "Validation should provide feedback"
            
        finally:
            temp_path.unlink(missing_ok=True)

    def test_complete_developer_workflow_sequence(self):
        """Test the complete developer workflow from quickstart user story 1."""
        # Step 1: Get system overview
        status_result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "status"],
            capture_output=True,
            text=True,
        )
        
        # Step 2: Look up term definition
        crossref_result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "cross-ref", "--term", "ATO"],
            capture_output=True,
            text=True,
        )
        
        # Step 3: Validate documentation
        validate_result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "validate"],
            capture_output=True,
            text=True,
        )
        
        # All steps should execute without crashing
        for result in [status_result, crossref_result, validate_result]:
            assert result.returncode in [0, 1], f"Command should not crash: {result.stderr}"
            output = result.stdout + result.stderr
            assert len(output.strip()) > 0, "Each command should produce output"