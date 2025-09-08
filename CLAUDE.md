# Claude Code Context: TransRapport Documentation Integration

## Project Overview
TransRapport is a local, offline-capable marker engine application that executes the LD-3.4 pipeline (ATO → SEM → CLU → MEMA). This documentation integration feature provides unified access and consistency validation for the four core documentation files.

## Current Feature: Documentation Integration (001-transrapport-md-and)
**Status**: Implementation planning complete  
**Branch**: `001-transrapport-md-and`

### Key Components
- **doc-validator library**: Core validation logic and cross-reference management
- **CLI integration**: Extends existing `me` command with `docs` subcommands
- **Documentation files**: TRANSRAPPORT.md, ARCHITECTURE.md, terminologie.md, MARKER.md

### Technology Stack
- **Language**: Python 3.11+
- **CLI**: Click framework
- **Storage**: SQLite (existing), local file system
- **Parsing**: PyYAML, regex
- **Testing**: pytest

### Architecture Principles
- **Offline-first**: No external dependencies or network calls
- **LD-3.4 compliant**: Follows marker pipeline specifications
- **CLI consistency**: Integrates with existing `me` command structure
- **Performance**: <2s validation, <100ms lookup

## File Structure
```
specs/001-transrapport-md-and/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan
├── research.md          # Technical research and decisions
├── data-model.md        # Entity definitions and relationships
├── quickstart.md        # User guide and testing scenarios
└── contracts/
    └── cli-interface.yaml   # CLI command contracts

terminologie/            # Documentation files to integrate
├── TRANSRAPPORT.md
├── ARCHITECTURE.md
├── terminologie.md
└── MARKER.md
```

## CLI Commands (Planned)
```bash
me docs validate [--strict] [--format json|text] [files...]
me docs cross-ref [--term TERM] [--file FILE] [--format json|text]
me docs status [--format json|text]
```

## Key Requirements
1. **FR-001**: Unified access to four core documentation files
2. **FR-002**: Maintain consistency in terminology across files
3. **FR-003**: Navigate between related concepts cross-documents
4. **FR-004**: Validate marker definitions comply with guidelines
5. **FR-005**: Reflect current LD-3.4 marker pipeline state

## Recent Changes
- 2025-09-08: Created feature specification and implementation plan
- 2025-09-08: Completed Phase 0 research and Phase 1 design artifacts
- 2025-09-08: Generated CLI contracts and quickstart documentation

## Next Steps
1. Execute `/tasks` command to generate task breakdown
2. Implement TDD approach: failing tests first
3. Build doc-validator library with CLI interface
4. Integration testing with existing TransRapport CLI

## Development Guidelines
- **TDD enforced**: Tests must be written and failing before implementation
- **Library-first**: Feature implemented as standalone library with CLI interface
- **No mocks**: Use real files and dependencies for integration tests
- **Observability**: Structured JSON logging for validation results

## Constitutional Compliance
✅ Single project structure  
✅ Direct framework usage (Click, PyYAML)  
✅ Library-first architecture planned  
✅ TDD approach documented  
✅ Real dependencies for testing  
✅ Structured logging included  
✅ Version 1.0.0 assigned