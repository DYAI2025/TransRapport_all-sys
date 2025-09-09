# Tasks: Cross-Platform Easy Installation

**Input**: Design documents from `/specs/004-app-must-be/`
**Prerequisites**: research.md, data-model.md, contracts/build-api.json, quickstart.md

## Execution Flow (main)
```
1. Load available design documents
   → research.md: Tauri v2 with platform-specific targets (.msi/.dmg/.deb/.rpm/.AppImage)
   → data-model.md: Installation Package, Build Configuration, Installation Session, System Registry Entry
   → contracts/build-api.json: /build, /package, /sign, /validate endpoints
   → quickstart.md: User stories for Windows/macOS/Linux installation flows
2. Generate tasks by category:
   → Setup: Tauri v2 config fix, toolchain consistency
   → Tests: Contract tests for all 4 endpoints, integration tests per platform
   → Core: CLI services implementation
   → Integration: Platform-specific build automation
   → Polish: Performance validation, code signing
3. Apply task rules:
   → Tauri config fixes are critical blockers (high priority)
   → Different contract files = parallel test creation [P]
   → Platform tests can run parallel [P]
   → Implementation follows tests (TDD)
4. Order by dependencies: Config fixes → Tests → Implementation → Integration → Polish
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## URGENT Phase 0: Critical Configuration Fix
**BLOCKER: Current Tauri config has v2 schema validation errors**
- [ ] T-FIX-001 [P] Update desktop/src-tauri/tauri.conf.json to Tauri v2 schema
  - Replace windows.wix: remove skipWebviewInstall/enableElevatedUpdateTask
  - Set bundle.windows.webviewInstallMode = {"type": "offlineInstaller", "silent": true}
  - Under linux.rpm: rename "requires" → "depends"  
  - Move "desktopTemplate" under linux.rpm (not appimage)
  - Keep targets: ["appimage","deb","rpm","nsis"]; remove "msi" on Linux runners

- [ ] T-FIX-002 [P] Ensure toolchain consistency in desktop/
  - Update tauri CLI to latest version
  - Run `tauri info` and capture output for dependency verification
  - Add nsis build dependencies on Ubuntu (if cross-building Windows)
  - Document that WiX/MSI builds run only on Windows runners

- [ ] T-FIX-003 Smoke build test with corrected configuration
  - Execute `tauri build` on Linux: expect appimage/deb/rpm success, nsis cross-build if configured
  - On failure: print schema validation errors verbatim and fix configuration issues
  - Verify all target formats generate successfully

- [ ] T-FIX-004 Open PR "fix/tauri-v2-config", merge when green
  - Create feature branch with configuration fixes
  - Ensure CI/CD pipeline passes with corrected schema
  - Merge to unblock remaining implementation tasks

## Phase 3.1: Setup (After Config Fix)
- [ ] T001 Verify current packaging library structure in src/lib/packaging/
- [ ] T002 Review implemented services: BuildService, PackageService, SignService, ValidateService
- [ ] T003 [P] Validate certificate management setup in certs/ directory structure

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests exist and currently pass - verifying implementation works correctly**
- [ ] T004 [P] Run contract test POST /build in tests/contract/test_build_api.py
- [ ] T005 [P] Run contract test POST /package in tests/contract/test_package_api.py  
- [ ] T006 [P] Run contract test POST /sign in tests/contract/test_sign_api.py
- [ ] T007 [P] Run contract test POST /validate in tests/contract/test_validate_api.py
- [ ] T008 [P] Run Windows MSI integration test in tests/integration/test_windows_install.py
- [ ] T009 [P] Run macOS DMG integration test in tests/integration/test_macos_install.py
- [ ] T010 [P] Run Linux packages integration test in tests/integration/test_linux_install.py
- [ ] T011 [P] Run cross-platform uninstall test in tests/integration/test_cross_platform_uninstall.py
- [ ] T012 [P] Run Windows user story test in tests/user_stories/test_windows_user_story.py
- [ ] T013 [P] Run macOS/Linux user story test in tests/user_stories/test_macos_linux_user_story.py

## Phase 3.3: Core Implementation (Services Already Implemented)
**NOTE: Services already implemented, verifying functionality**
- [ ] T014 Test BuildService with real Tauri build in src/lib/packaging/services/build_service.py
- [ ] T015 Test PackageService with artifact resolution in src/lib/packaging/services/package_service.py
- [ ] T016 Test SignService with certificate loading in src/lib/packaging/services/sign_service.py  
- [ ] T017 Test ValidateService with package validation in src/lib/packaging/services/validate_service.py
- [ ] T018 Verify CLI integration works correctly in src/cli/package_cli.py
- [ ] T019 Test data models serialization in src/lib/packaging/models.py

## Phase 3.4: Platform-Specific Integration
- [ ] T020 [P] Configure Windows MSI bundling in desktop/src-tauri/tauri.conf.json
- [ ] T021 [P] Configure macOS DMG bundling with proper icons and background
- [ ] T022 [P] Configure Linux DEB packaging with desktop file integration
- [ ] T023 [P] Configure Linux RPM packaging with proper dependencies
- [ ] T024 [P] Configure Linux AppImage with embedded dependencies
- [ ] T025 Set up GitHub Actions matrix build in .github/workflows/build.yml
- [ ] T026 Configure Azure Key Vault integration in certs/windows/config.json
- [ ] T027 Configure Apple Developer signing in certs/macos/config.json
- [ ] T028 Configure GPG signing for Linux in certs/linux/config.json

## Phase 3.5: Validation & Polish  
- [ ] T029 [P] Windows 11 installation validation test per quickstart.md
- [ ] T030 [P] macOS drag-to-Applications validation test per quickstart.md
- [ ] T031 [P] Linux package manager installation validation test per quickstart.md
- [ ] T032 [P] Linux AppImage universal installation validation test per quickstart.md
- [ ] T033 [P] Uninstallation verification test per quickstart.md
- [ ] T034 Performance benchmarks: installation <120s, package sizes <100MB
- [ ] T035 Code signing verification for all platforms
- [ ] T036 Build pipeline automation verification
- [ ] T037 Error scenario testing (disk space, permissions, corruption)

## Phase 3.6: Production Ready
- [ ] T038 [P] Update documentation in README.md and docs/
- [ ] T039 Create release artifacts and GitHub releases automation
- [ ] T040 Final integration test: complete build-sign-validate-install workflow

## Dependencies
- **CRITICAL**: T-FIX-001 through T-FIX-004 must complete before all other tasks
- Phase 3.2 tests (T004-T013) verify current implementation status
- Phase 3.3 (T014-T019) validates implemented services work correctly
- Phase 3.4 (T020-T028) requires Phase 3.3 completion
- Phase 3.5 (T029-T037) requires Phase 3.4 completion
- Phase 3.6 (T038-T040) requires all previous phases

## Critical Path Priority
1. **T-FIX-001 to T-FIX-004**: Fix Tauri v2 configuration (BLOCKER)
2. **T004-T007**: Verify contract tests pass with implemented services
3. **T008-T013**: Verify integration tests detect real installation issues
4. **T020-T024**: Platform-specific bundling configuration
5. **T029-T033**: User story validation tests

## Parallel Example
```
# After config fix, launch contract tests together:
Task: "Run contract test POST /build in tests/contract/test_build_api.py"
Task: "Run contract test POST /package in tests/contract/test_package_api.py"
Task: "Run contract test POST /sign in tests/contract/test_sign_api.py"
Task: "Run contract test POST /validate in tests/contract/test_validate_api.py"

# Platform configuration tasks can run parallel:
Task: "Configure Windows MSI bundling in desktop/src-tauri/tauri.conf.json"
Task: "Configure macOS DMG bundling with proper icons and background"  
Task: "Configure Linux DEB packaging with desktop file integration"
```

## Notes
- Current implementation is functional but needs Tauri v2 config fix
- All core services (Build/Package/Sign/Validate) are implemented
- CLI integration is complete and tested
- Focus on platform-specific bundling configuration and validation
- Real-world testing critical for user experience validation

## Task Generation Summary
*Applied during execution*

1. **From Contracts**: 4 endpoints → 4 contract test verification tasks [P]
2. **From Data Model**: 4 entities already implemented → validation tasks
3. **From User Stories**: 5 user scenarios → 5 integration validation tests [P] 
4. **From Research**: Platform-specific targets → configuration and build tasks [P]

## Validation Checklist
*Current Status*

- [x] All contracts have corresponding implemented services
- [x] All entities have model implementations
- [x] All tests written and executable (some failing due to config issues)
- [x] Service implementations completed and integrated
- [x] CLI provides full functionality
- [ ] Tauri v2 configuration corrected (CRITICAL BLOCKER)
- [ ] Platform-specific bundling configured
- [ ] Real installation flows validated