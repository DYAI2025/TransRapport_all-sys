# Data Model: Documentation Integration

## Core Entities

### DocumentationFile
Represents each of the four core documentation files with metadata and validation state.

**Fields**:
- `path`: str - Absolute path to the documentation file
- `name`: str - File identifier (e.g., "TRANSRAPPORT", "ARCHITECTURE")
- `version`: str - Last modified timestamp or content hash
- `size_bytes`: int - File size for change detection
- `last_validated`: datetime - When validation was last run
- `validation_status`: enum - VALID, INVALID, NOT_VALIDATED
- `dependencies`: List[str] - Files this document references

**Relationships**:
- Has many ValidationResult entries
- References other DocumentationFile entries via cross-references

### TerminologyEntry
Represents definitions from terminologie.md with usage tracking across documents.

**Fields**:
- `term`: str - The terminology term (e.g., "ATO", "SEM", "CLU", "MEMA")
- `definition`: str - The definition text from terminologie.md
- `aliases`: List[str] - Alternative forms of the term
- `category`: str - Term category (e.g., "marker_level", "cli_command")
- `usage_pattern`: str - Regex pattern for finding term usage

**Relationships**:
- Has many CrossReference entries showing usage locations

### CrossReference
Tracks usage of terminology and concepts across documentation files.

**Fields**:
- `term`: str - The referenced term
- `source_file`: str - File containing the reference
- `line_number`: int - Location in file
- `context`: str - Surrounding text for validation
- `reference_type`: enum - DEFINITION, USAGE, LINK
- `is_valid`: bool - Whether reference matches expected format

**Relationships**:
- Belongs to a TerminologyEntry
- Belongs to a DocumentationFile

### ValidationResult
Stores results of documentation validation checks.

**Fields**:
- `file_path`: str - Path to validated file
- `rule_name`: str - Name of validation rule that was applied
- `severity`: enum - ERROR, WARNING, INFO
- `line_number`: int - Location of issue (if applicable)
- `message`: str - Human-readable validation message
- `suggestion`: str - Suggested fix (optional)
- `validated_at`: datetime - When validation was performed

**Relationships**:
- Belongs to a DocumentationFile

### ArchitecturalComponent
Represents system components described across TRANSRAPPORT.md and ARCHITECTURE.md.

**Fields**:
- `component_name`: str - Component identifier (e.g., "CLI-Fassade", "ATO-Engine")
- `description`: str - Component purpose and functionality
- `source_files`: List[str] - Documents where component is described
- `dependencies`: List[str] - Other components this depends on
- `cli_commands`: List[str] - CLI commands associated with component

**Relationships**:
- References DocumentationFile entries
- Has dependencies on other ArchitecturalComponent entries

### MarkerDefinition
Represents marker specifications from MARKER.md with validation rules.

**Fields**:
- `marker_id`: str - Marker identifier (e.g., "ATO_EXAMPLE_SIGNAL")
- `marker_type`: enum - ATO, SEM, CLU, MEMA
- `definition_source`: str - Location in MARKER.md where defined
- `validation_rules`: List[str] - Rules that apply to this marker type
- `examples_required`: int - Minimum number of examples required
- `schema_constraints`: dict - Additional schema validation rules

**Relationships**:
- Belongs to DocumentationFile (MARKER.md)
- References TerminologyEntry for marker type definitions

## State Transitions

### DocumentationFile Validation States
```
NOT_VALIDATED → VALIDATING → VALID
                           → INVALID
VALID → VALIDATING (when file changes)
INVALID → VALIDATING (when revalidation requested)
```

### Cross-Reference Validation
```
NEW → CHECKING → VALID
               → INVALID → NEEDS_UPDATE
VALID → STALE (when source files change)
```

## Validation Rules

### Consistency Rules
1. **Terminology Usage**: All usage of defined terms must match definitions
2. **Cross-Reference Integrity**: All internal links must point to existing content
3. **CLI Command Consistency**: Commands referenced in docs must match actual CLI interface
4. **Marker Compliance**: Marker definitions must follow LD-3.4 specifications

### Format Rules
1. **Markdown Syntax**: Valid markdown structure
2. **Link Format**: Proper markdown link syntax for cross-references
3. **Code Block Consistency**: Code examples must be syntactically valid
4. **Header Structure**: Consistent heading hierarchy

### Content Rules
1. **Definition Completeness**: All technical terms must be defined
2. **Example Sufficiency**: Markers must have ≥5 examples as per LD-3.4
3. **Architectural Alignment**: Component descriptions must be consistent across files
4. **Version Consistency**: Referenced versions must match across documents