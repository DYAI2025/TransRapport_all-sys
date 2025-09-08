# Quickstart: Documentation Integration Feature

## Prerequisites
- TransRapport development environment set up
- Python 3.11+ with existing dependencies installed
- Four core documentation files present in expected locations:
  - `terminologie/TRANSRAPPORT.md`
  - `terminologie/ARCHITECTURE.md` 
  - `terminologie/terminologie.md`
  - `terminologie/MARKER.md`

## Installation
```bash
# Install additional CLI dependencies
pip install click

# Verify existing dependencies are available
python -c "import yaml, regex, sqlite3; print('Dependencies OK')"
```

## Basic Usage

### 1. Validate Documentation Consistency
```bash
# Basic validation of all documentation files
me docs validate

# Strict validation with JSON output
me docs validate --strict --format json

# Validate specific file
me docs validate terminologie/TRANSRAPPORT.md
```

Expected output (success):
```
✓ TRANSRAPPORT.md: Valid
✓ ARCHITECTURE.md: Valid  
✓ terminologie.md: Valid
✓ MARKER.md: Valid

Validation Summary:
- Files checked: 4
- Issues found: 0
- Status: PASS
```

Expected output (with issues):
```
✗ ARCHITECTURE.md: 2 issues found
  - Line 45: [ERROR] Undefined term 'CLU_INTUITION' (terminology-consistency)
  - Line 78: [WARNING] Broken cross-reference to 'MARKER.md#scoring-defaults' (cross-reference)

✓ TRANSRAPPORT.md: Valid
✓ terminologie.md: Valid  
✓ MARKER.md: Valid

Validation Summary:
- Files checked: 4
- Issues found: 2 (1 error, 1 warning)
- Status: FAIL
```

### 2. Check Cross-References
```bash
# Check all cross-references
me docs cross-ref

# Check references for specific term
me docs cross-ref --term "ATO"

# Check references in specific file
me docs cross-ref --file terminologie/ARCHITECTURE.md
```

Expected output:
```
Cross-Reference Report:

Terms Checked: 15
✓ ATO: 8 references, all valid
✓ SEM: 6 references, all valid
✗ MEMA: 4 references, 1 broken (ARCHITECTURE.md:123)
✓ CLU: 3 references, all valid

Broken Links:
- ARCHITECTURE.md:123 → 'terminologie.md#mema-definition' (target not found)

Summary: 21 references checked, 1 broken
```

### 3. Get Documentation Status
```bash
# Overall documentation status
me docs status

# JSON format for CI integration
me docs status --format json
```

Expected output:
```
Documentation Status Report

Files:
✓ TRANSRAPPORT.md        Last validated: 2025-09-08 10:15:32
✓ ARCHITECTURE.md        Last validated: 2025-09-08 10:15:32  
✓ terminologie.md        Last validated: 2025-09-08 10:15:32
✓ MARKER.md             Last validated: 2025-09-08 10:15:32

Statistics:
- Total terms defined: 47
- Total references: 156
- Broken references: 0
- Last full validation: 2025-09-08 10:15:32

Overall Status: VALID
```

## Integration with Development Workflow

### Pre-commit Validation
```bash
# Add to git pre-commit hook
#!/bin/bash
me docs validate --strict
if [ $? -ne 0 ]; then
    echo "Documentation validation failed. Please fix issues before committing."
    exit 1
fi
```

### CI/CD Integration
```bash
# In CI pipeline
me docs validate --strict --format json > docs-validation-report.json

# Check exit code
if [ $? -ne 0 ]; then
    echo "Documentation validation failed"
    exit 1
fi
```

## Testing the Feature

### User Story 1: Developer Understanding Architecture
```bash
# 1. Developer needs to understand overall system
me docs status
# Should show all files valid and provide overview

# 2. Developer looks for specific term definition
me docs cross-ref --term "ATO"  
# Should show all occurrences with consistent usage

# 3. Developer validates consistency after changes
echo "Test change" >> terminologie/TRANSRAPPORT.md
me docs validate
# Should detect change and re-validate
```

### User Story 2: Inconsistency Detection
```bash
# 1. Introduce terminology inconsistency
# Edit terminologie.md: Change "ATO" definition
# Edit ARCHITECTURE.md: Use old definition of "ATO"

# 2. Run validation
me docs validate --strict
# Should detect and report inconsistency with line numbers

# 3. Fix and revalidate
# Fix the inconsistency
me docs validate
# Should pass validation
```

### User Story 3: Cross-Reference Management
```bash
# 1. Add new cross-reference in ARCHITECTURE.md
echo "[New concept](terminologie.md#new-concept)" >> terminologie/ARCHITECTURE.md

# 2. Check for broken link
me docs cross-ref
# Should detect broken reference to non-existent section

# 3. Add missing definition and recheck
echo "## New Concept\nDefinition here." >> terminologie/terminologie.md
me docs cross-ref
# Should now show valid reference
```

## Performance Validation

### Response Time Requirements
```bash
# Validate performance goals
time me docs validate
# Should complete in < 2 seconds for 4 files

time me docs cross-ref --term "ATO"
# Should complete in < 100ms for term lookup

# Stress test with repeated validations
for i in {1..10}; do
    time me docs validate >/dev/null
done
# Average should be < 1 second
```

## Troubleshooting

### Common Issues

1. **"File not found" errors**
   ```bash
   # Check file locations
   find . -name "*.md" | grep -E "(TRANSRAPPORT|ARCHITECTURE|terminologie|MARKER)"
   ```

2. **"Invalid YAML" errors in marker files**
   ```bash
   # Validate YAML syntax separately
   python -c "import yaml; yaml.safe_load(open('markers/atomic/example.yaml'))"
   ```

3. **Performance issues**
   ```bash
   # Clear any cached data
   rm -rf ~/.cache/transrapport-docs/
   ```

### Debug Mode
```bash
# Enable verbose logging
me docs validate --debug
# Shows detailed parsing and validation steps
```

## Expected Integration Points

This feature integrates with:
- Existing `me` CLI command structure
- Current YAML marker validation system
- SQLite storage for metadata caching
- Standard TransRapport directory structure

Success criteria:
- All acceptance scenarios pass
- Performance requirements met
- No breaking changes to existing CLI
- Documentation files validated successfully