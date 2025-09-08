# Tasks: TransRapport Core Architecture Documentation Integration

**Input**: Design documents from `/specs/001-transrapport-md-and/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory - ✓ Python 3.11+, Click CLI, SQLite, PyYAML
2. Load design documents:
   → data-model.md: 6 entities → model tasks
   → contracts/cli-interface.yaml: 3 CLI commands → contract test tasks  
   → research.md: Click framework, regex parsing → setup tasks
3. Generate tasks by category:
   → Setup: doc-validator library, CLI integration, dependencies
   → Tests: CLI contract tests, integration tests for user stories
   → Core: models, validation services, CLI commands
   → Integration: existing CLI extension, SQLite schema
   → Polish: unit tests, performance validation, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Tests before implementation (TDD enforced)
5. Number tasks sequentially (T001-T030)
6. SUCCESS: 30 tasks ready for TDD execution
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Paths use single project structure: `src/`, `tests/`

## Phase 3.1: Setup
- [ ] T001 Create doc-validator library structure in src/doc_validator/ with __init__.py
- [ ] T002 Initialize Click CLI dependencies and update requirements.txt
- [ ] T003 [P] Configure pytest and linting tools for doc-validator library

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests [P]
- [ ] T004 [P] Contract test `me docs validate` CLI interface in tests/contract/test_docs_validate.py
- [ ] T005 [P] Contract test `me docs cross-ref` CLI interface in tests/contract/test_docs_crossref.py  
- [ ] T006 [P] Contract test `me docs status` CLI interface in tests/contract/test_docs_status.py

### Integration Tests [P] 
- [ ] T007 [P] Integration test developer understanding architecture workflow in tests/integration/test_developer_workflow.py
- [ ] T008 [P] Integration test inconsistency detection scenario in tests/integration/test_inconsistency_detection.py
- [ ] T009 [P] Integration test cross-reference management scenario in tests/integration/test_crossref_management.py

### Core Validation Tests [P]
- [ ] T010 [P] Test documentation file parsing and metadata extraction in tests/integration/test_doc_parsing.py
- [ ] T011 [P] Test terminology extraction from terminologie.md in tests/integration/test_terminology_parsing.py
- [ ] T012 [P] Test cross-reference validation across files in tests/integration/test_crossref_validation.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models [P]
- [ ] T013 [P] DocumentationFile model in src/doc_validator/models/documentation_file.py
- [ ] T014 [P] TerminologyEntry model in src/doc_validator/models/terminology_entry.py
- [ ] T015 [P] CrossReference model in src/doc_validator/models/cross_reference.py
- [ ] T016 [P] ValidationResult model in src/doc_validator/models/validation_result.py
- [ ] T017 [P] ArchitecturalComponent model in src/doc_validator/models/architectural_component.py
- [ ] T018 [P] MarkerDefinition model in src/doc_validator/models/marker_definition.py

### Services
- [ ] T019 DocumentationParser service in src/doc_validator/services/doc_parser.py
- [ ] T020 TerminologyExtractor service in src/doc_validator/services/terminology_extractor.py
- [ ] T021 CrossReferenceValidator service in src/doc_validator/services/crossref_validator.py
- [ ] T022 ValidationEngine service in src/doc_validator/services/validation_engine.py

### CLI Commands
- [ ] T023 `me docs validate` command implementation in src/doc_validator/cli/validate_command.py
- [ ] T024 `me docs cross-ref` command implementation in src/doc_validator/cli/crossref_command.py
- [ ] T025 `me docs status` command implementation in src/doc_validator/cli/status_command.py

## Phase 3.4: Integration
- [ ] T026 Integrate docs CLI commands with existing `me` command structure in src/cli/
- [ ] T027 Extend SQLite schema for documentation metadata caching
- [ ] T028 Add structured JSON logging for validation results

## Phase 3.5: Polish
- [ ] T029 [P] Performance validation tests (<2s validation, <100ms lookup) in tests/performance/test_performance.py
- [ ] T030 [P] Update CLAUDE.md with implementation details

## Dependencies
- Setup (T001-T003) before everything
- Tests (T004-T012) before implementation (T013-T028)
- Models (T013-T018) before Services (T019-T022)
- Services (T019-T022) before CLI Commands (T023-T025)
- CLI Commands (T023-T025) before Integration (T026-T028)
- Core complete before Polish (T029-T030)

## Parallel Execution Examples
```bash
# Phase 3.2: Launch contract tests together
Task: "Contract test me docs validate CLI interface in tests/contract/test_docs_validate.py"
Task: "Contract test me docs cross-ref CLI interface in tests/contract/test_docs_crossref.py"
Task: "Contract test me docs status CLI interface in tests/contract/test_docs_status.py"

# Phase 3.2: Launch integration tests together  
Task: "Integration test developer workflow in tests/integration/test_developer_workflow.py"
Task: "Integration test inconsistency detection in tests/integration/test_inconsistency_detection.py"
Task: "Integration test cross-reference management in tests/integration/test_crossref_management.py"

# Phase 3.3: Launch model creation together
Task: "DocumentationFile model in src/doc_validator/models/documentation_file.py"
Task: "TerminologyEntry model in src/doc_validator/models/terminology_entry.py" 
Task: "CrossReference model in src/doc_validator/models/cross_reference.py"
```

## Task Generation Rules Applied
1. **From Contracts**: 3 CLI commands → 3 contract test tasks [P]
2. **From Data Model**: 6 entities → 6 model creation tasks [P]
3. **From User Stories**: 3 quickstart scenarios → 3 integration test tasks [P]
4. **From Technical Context**: Click CLI, regex parsing, SQLite integration
5. **Ordering**: Setup → Tests → Models → Services → CLI → Integration → Polish

## Validation Checklist ✓
- [x] All contracts (3) have corresponding tests (T004-T006)
- [x] All entities (6) have model tasks (T013-T018)
- [x] All tests (T004-T012) come before implementation (T013-T028)
- [x] Parallel tasks [P] are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] TDD enforced: tests must fail before implementation

## Notes
- Follow constitutional TDD: RED-GREEN-Refactor cycle strictly enforced
- Leverage existing TransRapport patterns: SQLite, CLI structure, YAML parsing
- Performance targets: <2s validation, <100ms cross-reference lookup
- Integration with existing `me` command maintains consistency
- All tests use real files and dependencies (no mocks)