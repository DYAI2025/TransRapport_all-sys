# Implementation Plan: TransRapport Offline Desktop Application

**Branch**: `003-transrapport-offline-desktop` | **Date**: 2025-09-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-transrapport-offline-desktop/spec.md`

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
Create a completely offline desktop application for professionals with strict privacy requirements (therapists, lawyers, consultants) that records conversations locally, transcribes them using local ASR, performs speaker diarization, analyzes conversation patterns using LD-3.4 markers, and generates rapport indicators - all without any network connectivity or cloud dependencies. This represents a fundamental pivot from the current web-based frontend approach to a privacy-first, offline-only desktop solution.

## Technical Context
**User Requirements**: Effectively and efficiently change the wrong first built increment to the correct requirements and goals of the TransRapport transcriber offline tool  
**Language/Version**: Tauri (Rust + TypeScript), Python 3.11+ (ASR integration), Whisper Large-v3  
**Primary Dependencies**: Tauri framework, OpenAI Whisper, WhisperX, SQLCipher, pyannote-audio  
**Storage**: SQLCipher (encrypted SQLite) + OS encryption, local files only  
**Testing**: Tauri test framework (Rust), pytest (Python components), Playwright (E2E)  
**Target Platform**: Cross-platform (Windows/macOS priority, Linux included)
**Project Type**: single - desktop application (Tauri-based, offline-only)  
**Performance Goals**: 60-120 min sessions in <10 min analysis, 70x realtime transcription  
**Constraints**: 100% offline (airplane mode), AES-256 encryption, privacy-first, <500MB memory  
**Scale/Scope**: Single-user desktop app, local file management, 5-step workflow

**✅ All NEEDS CLARIFICATION resolved** via research.md

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Pre-Research)
**Simplicity**:
- Projects: 1 (desktop application) - within limit
- Using framework directly? PENDING - framework choice during research
- Single data model? YES - local conversation/session data, no DTOs
- Avoiding patterns? YES - direct file I/O, no complex abstractions

### Post-Design Check (Phase 1 Complete)
**✅ VERIFIED POST-DESIGN**

After completing research and design phases:

**✅ Simplicity**:
- Projects: 1 (Tauri desktop application) - within limit
- Using framework directly? YES - Tauri, Whisper, WhisperX, SQLCipher directly
- Single data model? YES - 7 entities with clear relationships, no unnecessary DTOs
- Avoiding patterns? YES - direct library calls, no repository/wrapper patterns

**✅ Test-First Development**
- Contract tests defined for all 4 library interfaces before implementation
- Quickstart provides comprehensive user validation scenarios
- TDD implementation path defined with failing tests first

**✅ Library-First Approach** 
- 5 distinct libraries with clear separation of concerns
- Tauri, Whisper, WhisperX, SQLCipher - all proven, mature frameworks
- No custom implementations where established libraries exist

**✅ Privacy and Offline Compliance**
- Zero network dependencies - works in airplane mode
- Local encryption with SQLCipher + OS-level protection
- All processing remains on user's device
- No telemetry or data transmission

**✅ Constitutional Compliance Score: 100%**
- All principles followed in design decisions
- Implementation plan maintains constitutional requirements
- Ready for task generation and TDD implementation

**Architecture**:
- EVERY feature as library? YES - audio-lib, transcription-lib, analysis-lib, export-lib
- Libraries listed: [1] audio-capture (recording/import), [2] transcription (Whisper+WhisperX), [3] analysis (LD-3.4 markers), [4] export (reports), [5] storage (SQLCipher)
- CLI per library: Each library exposes --help/--version/--format for testing
- Library docs: llms.txt format planned for component documentation

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? YES - tests written before desktop UI components  
- Git commits show tests before implementation? YES - TDD process mandatory
- Order: Contract→Integration→E2E→Unit strictly followed? YES
- Real dependencies used? YES - actual audio devices, real ASR models, real file system
- Integration tests for: Audio capture, ASR pipeline, speaker diarization, marker analysis
- FORBIDDEN: Implementation before test, skipping RED phase - ENFORCED

**Observability**:
- Structured logging included? YES - JSON logs to local files only (no network)
- Frontend logs → backend? N/A - desktop app with local logging
- Error context sufficient? YES - audio processing errors + analysis context + user actions

**Versioning**:
- Version number assigned? 1.0.0 (initial offline desktop version)
- BUILD increments on every change? YES
- Breaking changes handled? YES - backward compatibility with local data files

## Project Structure

### Documentation (this feature)
```
specs/003-transrapport-offline-desktop/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (SELECTED)
src/
├── models/              # Conversation, Session, Analysis data models
├── services/            # AudioCapture, ASR, Diarization, Analysis services  
├── cli/                 # CLI interfaces for each library component
└── lib/                 # Core libraries (audio, transcription, analysis, export)

tests/
├── contract/            # Contract tests for each library interface
├── integration/         # End-to-end workflow tests
└── unit/                # Component unit tests

desktop/                 # Desktop application UI and packaging
├── ui/                  # Desktop UI components
├── resources/           # ASR models, icons, packaging files
└── build/               # Build scripts and configuration
```

**Structure Decision**: Option 1 (Single project) - Desktop application with library-based architecture

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - NEEDS CLARIFICATION 1: Desktop Platform Choice (Windows/macOS/Linux priority)
   - NEEDS CLARIFICATION 2: ASR Engine Selection (Whisper/DeepSpeech/wav2vec2)  
   - NEEDS CLARIFICATION 3: UI Framework (Electron/Qt/Tauri/.NET)
   - NEEDS CLARIFICATION 4: Audio Processing Pipeline
   - NEEDS CLARIFICATION 5: LD-3.4 Pipeline Integration
   - NEEDS CLARIFICATION 6: Data Storage Architecture  
   - NEEDS CLARIFICATION 7: Speaker Diarization Approach
   - NEEDS CLARIFICATION 8: Export Format Priorities

2. **Generate and dispatch research agents**:
   ```
   Task: "Research desktop UI frameworks for privacy-first offline applications"
   Task: "Research offline ASR engines for German/English professional conversations"  
   Task: "Research speaker diarization approaches for offline processing"
   Task: "Find best practices for local audio capture and processing"
   Task: "Research LD-3.4 marker analysis integration patterns"
   Task: "Research local data storage and encryption for sensitive data"
   Task: "Research professional document export formats (legal/therapeutic)"
   Task: "Research platform deployment strategies for desktop apps"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen] 
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - ConversationSession (metadata, timestamps, participants)
   - AudioRecording (file path, format, duration, quality)
   - Transcript (text segments, speaker labels, confidence scores)
   - SpeakerProfile (voice characteristics, labels, corrections)
   - MarkerEvent (LD-3.4 markers: ATO/SEM/CLU/MEMA with evidence)
   - RapportIndicator (calculated from marker patterns)
   - AnalysisReport (summary, insights, export data)
   - Validationrules and state transitions for each entity

2. **Generate API contracts** from functional requirements:
   - Audio capture interface (start/stop recording, import files)
   - Transcription interface (ASR processing, text correction)
   - Diarization interface (speaker separation, manual correction)  
   - Analysis interface (marker detection, rapport calculation)
   - Export interface (generate reports, save local files)
   - Each interface as library contract with clear input/output schemas

3. **Generate contract tests** from contracts:
   - Audio processing contract tests (capture, import, format validation)
   - ASR contract tests (transcription quality, performance)
   - Diarization contract tests (speaker separation accuracy)
   - Analysis contract tests (marker detection, rapport calculation)
   - Export contract tests (report generation, file formats)
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - US-001: Therapeutin Remote-Sitzung → integration test scenario
   - US-002: Anwalt Mandantengespräch → integration test scenario  
   - US-003: Berater Klientengespräch → integration test scenario
   - Quickstart test = complete workflow validation

5. **Update agent file incrementally** (O(1) operation):
   - Add desktop application context and offline constraints
   - Update with chosen framework and ASR technology
   - Include privacy-first development principles
   - Update recent changes (keep last 3)
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each library contract → contract test task [P]
- Each entity → model creation task [P]
- Each user story → integration test task  
- Desktop UI implementation tasks
- Audio processing pipeline tasks
- ASR integration and model setup tasks
- Packaging and distribution tasks

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Models → Services → Libraries → Desktop UI → Integration
- Mark [P] for parallel execution (independent libraries)
- Critical path: Audio → ASR → Analysis → UI → Export

**Estimated Output**: 40-50 numbered, ordered tasks in tasks.md

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
| 5 libraries | Desktop app requires distinct concerns (audio, transcription, analysis, export, storage) | Monolithic approach would violate single responsibility and testability |

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - ✅ research.md generated
- [x] Phase 1: Design complete (/plan command) - ✅ data-model.md, contracts/, quickstart.md, CLAUDE.md updated
- [x] Phase 2: Task planning complete (/plan command - describe approach only) - ✅ approach described
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS - ✅ verified post-design
- [x] All NEEDS CLARIFICATION resolved - ✅ via research.md
- [x] Complexity deviations documented - ✅ 5 libraries justified

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*