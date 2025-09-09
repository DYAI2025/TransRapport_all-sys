# Claude Code Context: TransRapport Offline Desktop Application

## Project Overview
TransRapport is a local, offline-capable marker engine application that executes the LD-3.4 pipeline (ATO → SEM → CLU → MEMA). This desktop application provides completely offline transcription, speaker diarization, and conversation analysis for professionals with strict privacy requirements (therapists, lawyers, consultants).

## Current Feature: Cross-Platform Easy Installation (004-app-must-be)
**Status**: Design and contracts complete  
**Branch**: `004-app-must-be`

### Key Components
- **Cross-Platform Installers**: Native packages for Windows 11 (.msi), macOS (.dmg), Linux (.deb/.rpm/.AppImage)
- **Dependency Bundling**: All runtime dependencies packaged within installers
- **Code Signing Infrastructure**: Platform-specific certificates (EV for Windows, Apple Developer, GPG for Linux)
- **Build Automation**: GitHub Actions matrix for parallel cross-platform builds
- **Installation Validation**: VM-based testing across target platforms
- **User Experience**: Native OS conventions (installer wizards, drag-to-applications, package managers)

### Technology Stack
- **Desktop Framework**: Tauri (Rust + TypeScript/HTML frontend)
- **ASR Engine**: OpenAI Whisper Large-v3 with Python integration
- **Speaker Diarization**: WhisperX (integrated Whisper + pyannote)
- **Marker Analysis**: Existing LD-3.4 pipeline via library reuse
- **Data Storage**: SQLCipher + OS encryption hybrid approach
- **Audio Processing**: Dedicated Rust/Python audio libraries

### Architecture Principles
- **100% Offline Operation**: No network dependencies, works in airplane mode
- **Privacy First**: AES-256 encryption, local data only, no telemetry
- **Professional Quality**: >90% transcription accuracy, comprehensive marker analysis
- **Constitutional Compliance**: Library-first, test-first, no CLI modifications

## File Structure
```
desktop/
├── src-tauri/           # Rust backend
│   ├── audio/          # Audio capture and processing
│   ├── storage/        # SQLCipher database operations
│   └── analysis/       # Python integration for ASR/markers
├── src/                # Web frontend (TypeScript)
│   ├── components/     # UI components
│   ├── stores/         # State management
│   └── services/       # API communication
└── resources/          # Whisper models, templates, assets

src/
├── models/              # Conversation, Session, Analysis data models
├── services/            # AudioCapture, ASR, Diarization, Analysis services  
├── cli/                 # CLI interfaces for each library component
└── lib/                 # Core libraries (audio, transcription, analysis, export)

specs/003-transrapport-offline-desktop/
├── spec.md              # Feature specification
├── plan.md              # Complete implementation plan
├── research.md          # Technology decisions & rationale
├── data-model.md        # 7 core entities + validation rules
├── quickstart.md        # User scenarios & testing procedures
└── contracts/           # Library API contracts
    ├── audio-library.yaml       # Audio capture and import
    ├── transcription-library.yaml # Whisper ASR and diarization
    ├── analysis-library.yaml   # LD-3.4 marker analysis
    └── export-library.yaml     # Report generation and export
```

## Development Commands
```bash
# Desktop application development
cd desktop
npm install
npm run tauri:dev        # Development mode with hot reload
npm run tauri:build      # Production build

# Library development and testing  
cd src
cargo build              # Rust audio/storage libraries
python -m pytest tests/  # Python ASR/analysis libraries

# Integration testing
npm run test:integration  # Full workflow tests
npm run test:e2e         # End-to-end user scenario tests
```

## Key Requirements
1. **FR-001**: Offline audio recording and import (microphone + system audio)
2. **FR-002**: Local speech recognition with Whisper ASR (no cloud dependencies)
3. **FR-003**: Speaker diarization and manual correction capabilities
4. **FR-004**: LD-3.4 marker analysis (ATO→SEM→CLU→MEMA pipeline)
5. **FR-005**: Rapport indicator calculations from marker patterns
6. **FR-006**: Professional report generation with multiple templates
7. **FR-007**: Complete privacy protection with local encryption

## Data Model (7 Core Entities)
- **ConversationSession**: Professional conversation with metadata and consent
- **AudioRecording**: Local audio files with integrity validation
- **Transcript**: Speech-to-text with speaker segments and edit history
- **SpeakerProfile**: Voice characteristics and manual labels
- **MarkerEvent**: LD-3.4 marker detections with evidence and context
- **RapportIndicator**: Calculated communication dynamics and trends
- **AnalysisReport**: Professional reports with insights and recommendations

## Library Interfaces
**Audio Library**: Device management, recording, import, validation
**Transcription Library**: Whisper ASR, speaker diarization, edit support
**Analysis Library**: LD-3.4 markers, rapport calculations, validation
**Export Library**: Multi-format reports, templates, professional output

## Recent Changes
- 2025-09-09: Created cross-platform easy installation specification (004-app-must-be)
- 2025-09-09: Completed Phase 0 research: Tauri v2 bundling, code signing, cross-platform builds
- 2025-09-09: Completed Phase 1 design: Build API contracts, installer validation, platform-specific configs

## Next Steps
1. Execute `/tasks` command to generate task breakdown
2. Implement TDD approach: contract tests, integration tests, then implementation
3. Build Tauri desktop application with Rust audio/storage libraries
4. Integrate Python ASR/analysis libraries with desktop frontend
5. Professional user testing with real therapy/legal/consultation scenarios

## Development Guidelines
- **TDD enforced**: Tests must be written and failing before implementation
- **Library-first**: Use Tauri, Whisper, WhisperX, SQLCipher - no custom implementations
- **No mocks**: Use real audio devices, real ASR models, real file system, real encryption
- **Privacy focus**: No network calls, local encryption, secure deletion, audit trails
- **Professional quality**: >90% accuracy, comprehensive analysis, reliable operation

## Constitutional Compliance
✅ Single desktop application structure  
✅ Direct framework usage (Tauri, Whisper, SQLCipher)  
✅ Library-first architecture: 5 distinct libraries for separation of concerns  
✅ TDD approach with contract tests first for each library interface  
✅ Real dependencies: audio devices, ASR models, file system, LD-3.4 pipeline  
✅ Structured logging with local JSON files (no network)  
✅ Version 1.0.0 for initial offline desktop release  
✅ Performance: <500MB memory, 70x realtime transcription, <2s analysis feedback