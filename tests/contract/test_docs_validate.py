"""Contract test for 'me docs validate' CLI command."""
import json
import subprocess
import sys
from pathlib import Path


class TestDocsValidateContract:
    """Test contract for docs validate command."""

    def test_docs_validate_basic_help(self):
        """Test that 'me docs validate --help' works."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "validate", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "validate" in result.stdout.lower()

    def test_docs_validate_basic_execution(self):
        """Test that 'me docs validate' executes without error."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "validate"],
            capture_output=True,
            text=True,
        )
        # Should not crash, but may return non-zero if validation fails
        assert result.returncode in [0, 1]
        assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_docs_validate_strict_flag(self):
        """Test that 'me docs validate --strict' accepts the flag."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "validate", "--strict"],
            capture_output=True,
            text=True,
        )
        # Should not crash with unknown option
        assert "--strict" not in result.stderr or "no such option" not in result.stderr.lower()

    def test_docs_validate_json_format(self):
        """Test that 'me docs validate --format json' produces JSON output."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "validate", "--format", "json"],
            capture_output=True,
            text=True,
        )
        # Should not crash with unknown option
        assert "--format" not in result.stderr or "no such option" not in result.stderr.lower()
        
        # If successful, output should be parseable JSON
        if result.returncode == 0 and result.stdout.strip():
            try:
                json.loads(result.stdout)
            except json.JSONDecodeError:
                assert False, f"Output is not valid JSON: {result.stdout}"

    def test_docs_validate_specific_file(self):
        """Test that 'me docs validate <file>' accepts file argument."""
        # Create a test markdown file
        test_file = Path("test_doc.md")
        test_file.write_text("# Test Document\nThis is a test.")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "doc_validator.cli.main", "docs", "validate", str(test_file)],
                capture_output=True,
                text=True,
            )
            # Should accept the file argument without error about unknown options
            assert "no such option" not in result.stderr.lower()
        finally:
            test_file.unlink(missing_ok=True)

    def test_docs_validate_version(self):
        """Test that 'me --version' works."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1.0.0" in result.stdout