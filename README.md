# TransRapport Doc Validator

Documentation validation and cross-reference management for TransRapport marker pipeline.

## Features

- **Documentation Validation**: Validate markdown structure, content completeness, and syntax
- **Cross-Reference Checking**: Detect broken links and undefined terminology across files
- **Terminology Management**: Extract and validate terminology from `terminologie.md`
- **LD-3.4 Compliance**: Validate marker documentation against LD-3.4 specification
- **CLI Interface**: Simple command-line interface for validation workflows
- **Offline Operation**: No network dependencies - works entirely offline
- **Multiple Output Formats**: JSON and text output for integration with CI/CD

## Installation

### Prerequisites

- Python 3.11 or later
- pip (Python package manager)

### Quick Installation

```bash
curl -sSL https://raw.githubusercontent.com/transrapport/transrapport/main/install.sh | bash
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/transrapport/transrapport.git
cd transrapport
```

2. Run the installation script:
```bash
./install.sh
```

3. Verify installation:
```bash
transrapport-docs --version
```

## Usage

### Basic Validation

Validate all documentation in a directory:
```bash
transrapport-docs docs validate /path/to/documentation/
```

### Strict Mode

Enable strict validation (treats warnings as errors):
```bash
transrapport-docs docs validate --strict /path/to/documentation/
```

### JSON Output

Get validation results in JSON format:
```bash
transrapport-docs docs validate --format json /path/to/documentation/
```

### Validate Specific Files

Validate individual files:
```bash
transrapport-docs docs validate terminologie.md marker.md
```

## Output Format

### Text Output (Default)

```
ValidationEngine Results
=======================
✓ Validated 4 files successfully
⚠ Found 2 warnings, 0 errors

Issues:
└─ terminologie.md:15 [WARNING] Missing key marker terms: MEMA
   Suggestion: Add definitions for all marker levels (ATO, SEM, CLU, MEMA)

Summary: 2 warnings, 0 errors
```

### JSON Output

```json
{
  "success": true,
  "file_count": 4,
  "issues": [
    {
      "file_path": "terminologie.md",
      "rule_name": "terminology_completeness",
      "severity": "WARNING",
      "line_number": null,
      "message": "Missing key marker terms: MEMA",
      "suggestion": "Add definitions for all marker levels (ATO, SEM, CLU, MEMA)",
      "validated_at": "2025-01-15T10:30:45.123456"
    }
  ],
  "summary": {
    "errors": 0,
    "warnings": 2,
    "info": 0
  }
}
```

## Architecture

The validator consists of several key components:

- **ValidationEngine**: Orchestrates validation workflow
- **DocumentationParser**: Parses markdown files and extracts metadata
- **TerminologyExtractor**: Extracts terminology definitions from `terminologie.md`
- **CrossReferenceValidator**: Validates links and terminology usage across files
- **CLI Commands**: User interface via Click framework

## Validation Rules

### Markdown Structure
- Main title (# Title) at document start
- Proper markdown link syntax
- Balanced parentheses in links

### Content Completeness
- Minimum content length (100 characters)
- Required marker terms in `terminologie.md` (ATO, SEM, CLU, MEMA)
- LD-3.4 specification references in `marker.md`

### Cross-References
- Valid internal links between documentation files
- Defined terminology usage
- Valid CLI command references

## Development

### Development Setup

1. Clone and install in development mode:
```bash
git clone https://github.com/transrapport/transrapport.git
cd transrapport
pip install -e .[dev]
```

2. Run tests:
```bash
pytest
```

3. Run linting:
```bash
ruff check src/ tests/
black --check src/ tests/
```

### Project Structure

```
src/doc_validator/
├── cli/                 # CLI commands
├── models/             # Data models
├── services/           # Core validation services
└── __init__.py

tests/                  # Test suite
├── test_models/
├── test_services/
└── test_cli/
```

## Contributing

1. Follow test-driven development (TDD) practices
2. All tests must pass: `pytest`
3. Code must be properly formatted: `black src/ tests/`
4. Code must pass linting: `ruff check src/ tests/`
5. Follow the existing code style and patterns

## License

This project is licensed under CC BY-NC-SA 4.0. See the license details in `pyproject.toml`.

## Support

For bugs and feature requests, please open an issue on the GitHub repository.

For questions about TransRapport marker pipeline and LD-3.4 specification, refer to the project documentation.