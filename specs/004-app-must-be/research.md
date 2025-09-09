# Cross-Platform Native Installer Research

## 1. Tauri Bundling Platform Strategy

**Decision**: Use Tauri v2 with platform-specific bundle targets (.msi/.exe for Windows, .dmg/.app for macOS, .deb/.rpm/.AppImage for Linux)

**Rationale**: 
- Single configuration file manages all platform-specific settings
- Built-in WebView2 runtime handling with embedding/bootstrapping options
- AppImage format eliminates Linux distribution complexity by bundling all dependencies
- Proven production stability with major applications using Tauri for distribution

**Alternatives Considered**:
- Electron with electron-builder: Rejected due to higher memory footprint (200MB+ vs 50MB) and larger bundle sizes
- Qt/C++ cross-compilation: Rejected due to steep learning curve and complex UI development
- .NET MAUI: Rejected due to limited Linux support and Microsoft ecosystem dependency

## 2. Code Signing and Security

**Decision**: Platform-specific certificate strategy with cloud HSM integration

**Rationale**:
- 2024 requirements mandate EV certificates stored in HSMs for Windows to avoid security warnings
- Azure Trusted Signing provides managed solution reducing certificate management overhead
- Timestamping ensures signature validity beyond certificate expiration
- Each platform requires distinct certificates (EV/OV for Windows, Apple Developer for macOS, optional GPG for Linux)

**Alternatives Considered**:
- Self-signed certificates: Rejected due to security warnings that block non-technical users
- Manual certificate management: Rejected due to error-prone process and CI/CD incompatibility
- Single certificate authority: Not technically feasible across platforms

## 3. Dependency Bundling Strategy

**Decision**: Static bundling with runtime detection for optimal user experience

**Rationale**:
- Eliminates user prerequisite installation, crucial for non-technical users
- AppImage bundles all dependencies including media frameworks
- WebView2 bootstrapper balances bundle size vs reliability
- Reduces support burden by ensuring consistent runtime environment

**Alternatives Considered**:
- Dynamic linking: Rejected due to requiring user-installed dependencies
- Full embedded runtime: Rejected due to 180MB+ size increase for WebView2
- Package manager dependencies: Rejected due to inconsistent Linux distribution support

## 4. Installation User Experience

**Decision**: Native platform conventions with minimal user interaction

**Rationale**:
- Windows MSI with standard wizard flow familiar to users
- macOS DMG with drag-to-Applications metaphor following Apple guidelines
- Linux distribution-specific packages for system integration, AppImage for universal compatibility
- Follows platform conventions that users already understand

**Alternatives Considered**:
- Unified installer experience: Rejected as it violates platform conventions
- Command-line installation: Rejected as not accessible to target users
- Web-based installer: Rejected due to security concerns and network dependency

## 5. Build Automation Strategy

**Decision**: GitHub Actions with platform matrix strategy

**Rationale**:
- Native runners for each platform ensure authentic build environments
- Parallel execution reduces build time to under 5 minutes
- Integrated artifact management and release automation
- Free for public repositories, cost-effective scaling

**Alternatives Considered**:
- Self-hosted runners: Rejected due to infrastructure maintenance overhead
- CircleCI/GitLab CI: Rejected to avoid additional service dependencies
- Manual build process: Rejected due to scalability and consistency issues

## 6. Testing and Validation Approach

**Decision**: Multi-tier automated testing with VM-based validation

**Rationale**:
- VM testing ensures clean installation environments matching user scenarios
- Automated regression testing catches 80% of issues in development cycle
- Cross-platform cloud infrastructure provides comprehensive device coverage
- CI/CD integration enables continuous installer validation

**Alternatives Considered**:
- Manual testing only: Rejected due to scalability and consistency issues
- Single-platform testing: Rejected as it misses platform-specific integration issues
- Post-release testing: Rejected due to high cost of fixing distributed issues

## 7. File Association and Desktop Integration

**Decision**: Declarative configuration through Tauri bundler with platform-specific metadata

**Rationale**:
- Automatic desktop file generation following freedesktop.org specifications
- Windows registry integration through MSI installer
- macOS Info.plist configuration for seamless file type associations
- Ensures proper application discovery in OS menus and file managers

**Alternatives Considered**:
- Runtime registration: Rejected due to requiring elevated privileges
- Manual user configuration: Rejected due to poor user experience
- Web-based file handling: Rejected due to limited functionality

## Implementation Recommendations

### Phase 1: Basic Cross-Platform Bundling
- Configure Tauri for .msi, .dmg, .deb, .rpm, and .AppImage targets
- Implement dependency bundling for each platform
- Create basic desktop integration (icons, menu entries)

### Phase 2: Security and Signing Infrastructure  
- Set up Azure Key Vault for Windows code signing
- Configure Apple Developer certificate handling
- Implement GPG signing for Linux packages

### Phase 3: Automated Build Pipeline
- GitHub Actions workflow with platform matrix
- Artifact management and release automation
- Integration with certificate management

### Phase 4: Testing and Validation
- VM-based installation testing
- Automated uninstaller validation
- Performance and startup time benchmarks

## Technical Configuration Summary

**Bundle Targets**: `["msi", "nsis", "app", "dmg", "deb", "rpm", "appimage"]`
**WebView Strategy**: Bootstrapper download for optimal balance
**Dependency Handling**: Static bundling with platform-specific package requirements
**Code Signing**: Azure Trusted Signing (Windows), Apple certificates (macOS), GPG (Linux)
**Build Platform**: GitHub Actions with native runners
**Testing Strategy**: Automated VM validation with cross-platform coverage