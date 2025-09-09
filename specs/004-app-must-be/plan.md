# Implementation Plan: Cross-Platform Easy Installation

**Branch**: `004-app-must-be` | **Date**: 2025-09-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-app-must-be/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Create native installer packages for TransRapport constitutional analysis application that enable non-technical users to easily install on Windows 11, macOS, and Linux distributions. The installation must be intuitive, self-contained (bundling all dependencies), and result in a fully functional application accessible through standard OS application menus. Technical approach involves Tauri desktop framework for cross-platform bundling with OS-specific installer generation.

## Technical Context
**Language/Version**: Rust (Tauri backend), TypeScript/Svelte (frontend), Python 3.11 (CLI integration)  
**Primary Dependencies**: Tauri v1.x, Svelte 4, Vite, Node.js 18+, Rust toolchain  
**Storage**: Existing SQLCipher encrypted database (already implemented)  
**Testing**: cargo test (Rust), Jest/Vitest (TypeScript), pytest (Python CLI)  
**Target Platform**: Windows 11 (.msi), macOS (.dmg), Linux (.deb/.rpm/.AppImage)
**Project Type**: Desktop application - cross-platform native installer generation  
**Performance Goals**: <5 second installation startup, <200MB installer size, <10 second first launch  
**Constraints**: Offline-capable, no network dependencies, bundle all runtime dependencies, non-technical user friendly  
**Scale/Scope**: Single desktop application with 3 platform targets, automated build pipeline, code signing [NEEDS CLARIFICATION: certificates]

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 2 (desktop app, build pipeline)
- Using framework directly? (yes, Tauri native bundling)
- Single data model? (yes, existing SQLCipher schema reused)
- Avoiding patterns? (yes, direct Tauri build configs, no custom wrappers)

**Architecture**:
- EVERY feature as library? (builds on existing TransRapport libraries)
- Libraries listed: packaging-lib (installer generation), build-pipeline (CI/CD integration)
- CLI per library: [package-app --platform=all --sign, build-installer --target=windows]
- Library docs: llms.txt format planned? (yes, for packaging library)

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? (yes, installer tests must fail before build configs)
- Git commits show tests before implementation? (yes, test actual installation process)
- Order: Contract→Integration→E2E→Unit strictly followed? (yes, contract=build specs, integration=platform installs)
- Real dependencies used? (yes, actual OS package managers and installation flows)
- Integration tests for: installer generation, platform-specific installation, uninstallation
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included?
- Frontend logs → backend? (unified stream)
- Error context sufficient?

**Versioning**:
- Version number assigned? (MAJOR.MINOR.BUILD)
- BUILD increments on every change?
- Breaking changes handled? (parallel tests, migration plan)

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 1 (Single project) - Desktop application with packaging extensions

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `/scripts/update-agent-context.sh [claude|gemini|copilot]` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (build-api contracts, installer data model, quickstart validation)
- Each build API endpoint → contract test task [P] (build, package, sign, validate)
- Each installer platform → package generation task [P] (Windows MSI, macOS DMG, Linux packages)
- Each user story → integration test task (installation validation across platforms)
- Implementation tasks to make contract tests pass (Tauri build configs, signing infrastructure)
- Automation tasks for CI/CD pipeline with GitHub Actions matrix

**Ordering Strategy**:
- TDD order: Contract tests for build API before implementation
- Platform order: Build pipeline before platform-specific installers before signing
- Dependency order: Basic bundling before advanced features before automation
- Mark [P] for parallel execution (independent platform builds)

**Estimated Output**: 20-25 numbered, ordered tasks focusing on installer generation and validation

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*