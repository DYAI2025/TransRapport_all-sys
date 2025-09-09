# Data Model: Frontend Architecture for TransRapport Backend Interaction

**Feature**: Frontend Architecture for TransRapport Backend Interaction  
**Date**: 2025-09-09  
**Source**: Extracted from feature specification and research findings

## Core Entities

### ValidationSession

**Purpose**: Represents a user-initiated validation process with associated files, settings, and results

**Attributes**:
- `id: string` - Unique session identifier (UUID)
- `userId: string | null` - User identifier (future multi-user support)
- `status: SessionStatus` - Current session state
- `command: string` - CLI command being executed
- `workingDirectory: string` - Target directory for validation
- `settings: ValidationSettings` - Validation configuration
- `startedAt: Date` - Session creation timestamp
- `completedAt: Date | null` - Session completion timestamp
- `progress: SessionProgress` - Current progress information
- `results: ValidationResult[]` - Array of validation results
- `output: OutputLine[]` - Captured CLI output lines

**Relationships**:
- One-to-many with ValidationResult
- One-to-many with OutputLine
- One-to-one with ValidationSettings

**State Transitions**:
```
idle → running → completed
idle → running → failed  
idle → running → cancelled
running → paused → running
```

**Validation Rules**:
- `id` must be unique across all sessions
- `status` transitions must follow allowed state machine
- `completedAt` can only be set when status is completed/failed/cancelled
- `command` must be valid TransRapport CLI command

### DocumentationProject

**Purpose**: Collection of related documentation files that are validated together as a unit

**Attributes**:
- `id: string` - Project unique identifier
- `name: string` - Human-readable project name
- `rootPath: string` - Absolute path to project root
- `lastValidated: Date | null` - Timestamp of most recent validation
- `fileCount: number` - Total number of documentation files
- `validationStatus: ProjectStatus` - Overall project validation status
- `settings: ValidationSettings` - Project-specific validation settings
- `createdAt: Date` - Project creation timestamp
- `updatedAt: Date` - Last modification timestamp

**Relationships**:
- One-to-many with ValidationSession
- One-to-many with DocumentationFile (via file system)

**Validation Rules**:
- `name` must be 1-100 characters, no special characters
- `rootPath` must be valid, accessible directory path
- `fileCount` must be non-negative integer
- Projects cannot share the same rootPath

### ValidationResult

**Purpose**: Structured data containing errors, warnings, cross-references, and terminology analysis from backend processing

**Attributes**:
- `id: string` - Result unique identifier
- `sessionId: string` - Associated validation session
- `file: string` - File path relative to project root
- `rule: string` - Validation rule that generated this result
- `severity: ResultSeverity` - Error/Warning/Info level
- `lineNumber: number | null` - Line number where issue was found
- `message: string` - Human-readable issue description
- `suggestion: string` - Recommended fix or improvement
- `validatedAt: Date` - Timestamp when validation occurred
- `context: string | null` - Surrounding code/text context

**Relationships**:
- Many-to-one with ValidationSession
- References DocumentationFile (via file path)

**Validation Rules**:
- `severity` must be ERROR, WARNING, or INFO
- `lineNumber` must be positive integer if provided
- `message` and `suggestion` must be non-empty strings
- `file` must be relative path within project

### UserProfile

**Purpose**: User preferences, project access rights, and session history

**Attributes**:
- `id: string` - User unique identifier
- `username: string` - Display name
- `email: string | null` - Contact email (future feature)
- `preferences: UserPreferences` - UI and validation preferences
- `projects: string[]` - Array of accessible project IDs
- `recentSessions: string[]` - Recently accessed session IDs (max 10)
- `createdAt: Date` - Account creation timestamp
- `lastLoginAt: Date` - Most recent access timestamp

**Relationships**:
- One-to-many with ValidationSession
- Many-to-many with DocumentationProject (via projects array)

**Validation Rules**:
- `username` must be 3-50 characters, alphanumeric + underscore
- `email` must be valid email format if provided
- `recentSessions` max 10 items, LIFO order
- `projects` contains only valid project IDs

### ExportReport

**Purpose**: Generated output containing validation results in user-requested format for sharing or archival

**Attributes**:
- `id: string` - Report unique identifier  
- `sessionId: string` - Source validation session
- `format: ExportFormat` - Output format (JSON/HTML/PDF)
- `fileName: string` - Generated file name
- `size: number` - File size in bytes
- `createdAt: Date` - Report generation timestamp
- `expiresAt: Date` - When report will be deleted
- `downloadCount: number` - Number of times downloaded
- `status: ExportStatus` - Generation status

**Relationships**:
- Many-to-one with ValidationSession

**Validation Rules**:
- `format` must be JSON, HTML, or PDF
- `fileName` must have appropriate extension for format
- `size` must be positive integer
- `expiresAt` must be after `createdAt`
- `downloadCount` must be non-negative

## Supporting Types

### Enums

```typescript
enum SessionStatus {
  IDLE = 'idle',
  RUNNING = 'running', 
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

enum ProjectStatus {
  UNKNOWN = 'unknown',
  VALID = 'valid',
  WARNINGS = 'warnings', 
  ERRORS = 'errors',
  PROCESSING = 'processing'
}

enum ResultSeverity {
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info'
}

enum ExportFormat {
  JSON = 'json',
  HTML = 'html', 
  PDF = 'pdf'
}

enum ExportStatus {
  GENERATING = 'generating',
  READY = 'ready',
  FAILED = 'failed',
  EXPIRED = 'expired'
}
```

### Complex Types

```typescript
interface ValidationSettings {
  strict: boolean;
  format: 'json' | 'text';
  filePatterns: string[];
  excludePatterns: string[];
  timeoutSeconds: number;
  maxFileSize: number;
}

interface SessionProgress {
  stage: string;
  percentage: number;
  currentFile: string | null;
  totalFiles: number | null;
  processedFiles: number;
  errorsFound: number;
  warningsFound: number;
}

interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  defaultValidationSettings: ValidationSettings;
  autoSaveResults: boolean;
  notificationEnabled: boolean;
  maxRecentSessions: number;
}

interface OutputLine {
  timestamp: Date;
  stream: 'stdout' | 'stderr';
  content: string;
  lineNumber: number;
}
```

## Data Flow Patterns

### Validation Workflow
1. User creates ValidationSession with settings
2. Backend starts CLI subprocess and streams output
3. OutputLines accumulated in real-time via WebSocket
4. ValidationResults parsed from CLI JSON output 
5. SessionProgress updated throughout process
6. Final results stored and session marked complete

### Project Management
1. User creates DocumentationProject from directory
2. System scans for .md files and updates fileCount
3. Validation sessions associated with project
4. Project status updated based on latest validation results
5. Historical validation data maintained per project

### Export Generation
1. User requests export from completed ValidationSession
2. ExportReport entity created with GENERATING status
3. Backend formats results according to requested format
4. Report file generated and stored temporarily
5. ExportReport updated with READY status and download link
6. Reports auto-expire after configured period

## Storage Strategy

### Backend Storage
- **SQLite Database**: Session metadata, user profiles, project info
- **File System**: Generated export reports, temporary CLI output
- **Memory**: Active WebSocket sessions, real-time state

### Frontend Storage  
- **Browser LocalStorage**: User preferences, recent project list
- **Session Storage**: Current session data, UI state
- **Memory**: Real-time validation results, WebSocket message cache

### Data Persistence
- ValidationSessions: Persist for 30 days
- ValidationResults: Persist with sessions
- ExportReports: Auto-delete after 7 days
- UserProfiles: Persist indefinitely
- DocumentationProjects: Persist until user deletion

## Performance Considerations

### Scalability Limits
- Max 100 concurrent ValidationSessions per instance
- Max 10,000 ValidationResults per session
- Max 1,000 OutputLines per session (with rotation)
- Max 50 DocumentationProjects per user

### Optimization Strategies
- Lazy loading of ValidationResults (pagination)
- OutputLine rotation for long-running sessions
- Background cleanup of expired ExportReports
- Database indexes on frequently queried fields
- Caching of project metadata and settings

---

**Data Model Status**: Complete  
**Entity Count**: 5 core entities + 5 supporting types  
**Validation Rules**: Comprehensive business logic defined  
**Ready for**: API contract generation and implementation