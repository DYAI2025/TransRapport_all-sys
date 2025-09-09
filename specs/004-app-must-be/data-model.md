# Data Model: Cross-Platform Easy Installation

## Core Entities

### Installation Package
**Purpose**: Represents a platform-specific installer bundle containing the application and all dependencies
**Attributes**:
- `platform`: Target platform (windows-11, macos, linux-deb, linux-rpm, linux-appimage)
- `version`: Application version (MAJOR.MINOR.BUILD format)
- `bundle_type`: Package format (msi, exe, dmg, app, deb, rpm, appimage)
- `file_size`: Package size in bytes
- `checksum`: SHA256 hash for integrity verification  
- `dependencies_bundled`: List of bundled runtime dependencies
- `signature_status`: Code signing validation status
- `creation_timestamp`: Build timestamp
- `target_architecture`: CPU architecture (x64, arm64, universal)

**Validation Rules**:
- Platform must be one of supported targets
- Version must follow semantic versioning
- File size must not exceed platform limits (4GB for MSI)
- Checksum must be valid SHA256
- Signature status required for Windows/macOS packages

### Build Configuration
**Purpose**: Defines platform-specific build settings and bundling parameters
**Attributes**:
- `tauri_config`: Platform-specific Tauri bundle configuration
- `signing_config`: Code signing certificate and key management
- `bundle_options`: Platform-specific bundling options
- `file_associations`: MIME types and file extensions to register
- `desktop_integration`: Menu entries, icons, shortcuts configuration
- `dependency_manifest`: Required runtime libraries per platform
- `installer_customization`: Platform-specific UI customization

**Validation Rules**:
- Tauri config must validate against schema
- Signing config required for production builds
- File associations must follow platform conventions
- Desktop integration must include required metadata

### Installation Session
**Purpose**: Tracks an individual installation attempt on a user system
**Attributes**:
- `session_id`: Unique identifier for installation attempt
- `package_info`: Reference to Installation Package
- `target_system`: OS version and architecture details
- `installation_path`: Target directory for application files
- `status`: Installation state (pending, in_progress, completed, failed, cancelled)
- `start_time`: Installation start timestamp
- `end_time`: Installation completion timestamp
- `error_details`: Error messages and diagnostic information
- `rollback_info`: Data needed for uninstallation cleanup
- `validation_results`: Post-installation verification results

**State Transitions**:
- `pending` → `in_progress` (installation started)
- `in_progress` → `completed` (successful installation)
- `in_progress` → `failed` (installation error occurred)
- `in_progress` → `cancelled` (user cancelled installation)
- `completed` → `pending` (reinstallation scenario)

**Validation Rules**:
- Session ID must be globally unique
- Target system must meet minimum requirements
- Installation path must be writable
- Error details required when status is 'failed'

### System Registry Entry
**Purpose**: Represents OS-specific registration for application discovery and uninstallation
**Attributes**:
- `registry_type`: Platform registry system (windows_registry, macos_plist, linux_desktop)
- `application_id`: Unique application identifier
- `display_name`: Application name shown in OS menus
- `version`: Installed version
- `install_location`: Application installation directory
- `uninstall_command`: Command to remove application
- `icon_path`: Application icon location
- `file_associations`: Registered file type handlers
- `menu_entries`: Created menu/launcher entries

**Validation Rules**:
- Application ID must be unique per system
- Uninstall command must be executable
- Icon path must be valid and accessible
- Menu entries must follow platform conventions

## Entity Relationships

- **Installation Package** → **Build Configuration** (one-to-one): Each package created from specific build config
- **Installation Package** → **Installation Session** (one-to-many): Package can be installed multiple times
- **Installation Session** → **System Registry Entry** (one-to-many): Installation creates multiple registry entries
- **Build Configuration** → **Installation Package** (one-to-many): Config can generate packages for multiple platforms

## Data Flow

1. **Build Phase**: Build Configuration → Installation Package creation
2. **Distribution Phase**: Installation Package → User download
3. **Installation Phase**: Installation Package → Installation Session → System Registry Entry
4. **Uninstallation Phase**: System Registry Entry → cleanup and removal

## Validation Context

**Installation Compatibility**:
- Target system must meet minimum OS version requirements
- Available disk space must exceed package size + 20% buffer
- User must have required permissions for installation directory
- No conflicting versions already installed

**Security Validation**:
- Package signature must be valid and trusted
- Checksum must match expected value  
- Certificate must not be expired or revoked
- Source must be from trusted distribution channel