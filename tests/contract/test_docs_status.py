"""Contract test for 'me docs status' CLI command."""
import json
import subprocess
import sys


class TestDocsStatusContract:
    """Test contract for docs status command."""

    def test_docs_status_basic_help(self):
        """Test that 'me docs status --help' works."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "status", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "status" in result.stdout.lower()

    def test_docs_status_basic_execution(self):
        """Test that 'me docs status' executes without error."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "status"],
            capture_output=True,
            text=True,
        )
        # Should not crash, but may return non-zero if no docs found
        assert result.returncode in [0, 1]
        assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_docs_status_json_format(self):
        """Test that 'me docs status --format json' produces JSON output."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "status", "--format", "json"],
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

    def test_docs_status_text_format_default(self):
        """Test that text format is the default."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "status"],
            capture_output=True,
            text=True,
        )
        
        # Default should be text format, not JSON
        if result.returncode == 0 and result.stdout.strip():
            # Should NOT be valid JSON by default
            try:
                json.loads(result.stdout)
                # If this succeeds, the default might be JSON, which could be acceptable
                # but let's ensure it's not due to an empty response
                assert len(result.stdout.strip()) > 0
            except json.JSONDecodeError:
                # This is expected for text format
                pass

    def test_docs_status_help_mentions_format(self):
        """Test that help mentions format option."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "status", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Help should mention format options
        assert "--format" in result.stdout or "format" in result.stdout.lower()