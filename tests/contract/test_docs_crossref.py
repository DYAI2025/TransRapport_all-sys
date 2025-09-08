"""Contract test for 'me docs cross-ref' CLI command."""
import json
import subprocess
import sys


class TestDocsCrossRefContract:
    """Test contract for docs cross-ref command."""

    def test_docs_crossref_basic_help(self):
        """Test that 'me docs cross-ref --help' works."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "cross-ref", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "cross-ref" in result.stdout.lower() or "reference" in result.stdout.lower()

    def test_docs_crossref_basic_execution(self):
        """Test that 'me docs cross-ref' executes without error."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "cross-ref"],
            capture_output=True,
            text=True,
        )
        # Should not crash, but may return non-zero if no docs found
        assert result.returncode in [0, 1]
        assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_docs_crossref_term_flag(self):
        """Test that 'me docs cross-ref --term ATO' accepts the term flag."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "cross-ref", "--term", "ATO"],
            capture_output=True,
            text=True,
        )
        # Should not crash with unknown option
        assert "--term" not in result.stderr or "no such option" not in result.stderr.lower()

    def test_docs_crossref_file_flag(self):
        """Test that 'me docs cross-ref --file <file>' accepts the file flag."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "doc_validator.cli.main",
                "docs",
                "cross-ref",
                "--file",
                "terminologie/TRANSRAPPORT.md",
            ],
            capture_output=True,
            text=True,
        )
        # Should not crash with unknown option
        assert "--file" not in result.stderr or "no such option" not in result.stderr.lower()

    def test_docs_crossref_json_format(self):
        """Test that 'me docs cross-ref --format json' produces JSON output."""
        result = subprocess.run(
            [sys.executable, "-m", "doc_validator.cli.main", "docs", "cross-ref", "--format", "json"],
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

    def test_docs_crossref_combined_flags(self):
        """Test that combined flags work together."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "doc_validator.cli.main",
                "docs",
                "cross-ref",
                "--term",
                "ATO",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
        )
        # Should accept both flags without unknown option errors
        assert "no such option" not in result.stderr.lower()