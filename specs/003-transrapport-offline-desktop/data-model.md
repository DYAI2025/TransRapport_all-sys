# Data Model: TransRapport Offline Desktop Application

**Feature**: TransRapport Offline Desktop Application  
**Date**: 2025-09-08  
**Source**: Extracted from feature specification and research findings

## Core Entities

### ConversationSession

**Purpose**: Represents a complete professional conversation session with metadata, timestamps, and participant information

**Attributes**:
- `id: string` - Unique session identifier (UUID)
- `name: string` - User-defined session name (e.g., "Client Meeting - 2025-09-08")
- `clientReference: string | null` - Client/case reference number for professional organization
- `sessionType: SessionType` - Type of session (therapy, legal, consultation)
- `startedAt: DateTime` - Session start timestamp
- `endedAt: DateTime | null` - Session completion timestamp
- `duration: number | null` - Session duration in seconds
- `location: string | null` - Session location (office, remote, etc.)
- `consentGiven: boolean` - Explicit consent for recording and analysis
- `consentDetails: string | null` - Consent documentation details
- `notes: string | null` - User notes about the session
- `status: SessionStatus` - Current session state
- `privacy: PrivacyLevel` - Privacy/confidentiality level
- `createdAt: DateTime` - Record creation timestamp
- `updatedAt: DateTime` - Last modification timestamp

**Relationships**:
- One-to-one with AudioRecording
- One-to-one with Transcript
- One-to-many with SpeakerProfile
- One-to-many with MarkerEvent
- One-to-many with RapportIndicator
- One-to-one with AnalysisReport

**State Transitions**:
```
created → recording → processing → completed
created → recording → cancelled
processing → failed
completed → archived
```

**Validation Rules**:
- `id` must be unique across all sessions
- `name` must be 1-200 characters
- `startedAt` cannot be in the future
- `endedAt` must be after `startedAt` if provided
- `consentGiven` must be true before processing
- `status` transitions must follow allowed state machine

### AudioRecording

**Purpose**: Contains audio file metadata and recording parameters for the conversation

**Attributes**:
- `id: string` - Unique recording identifier (UUID)
- `sessionId: string` - Associated conversation session
- `filePath: string` - Local file system path to audio file
- `fileName: string` - Original file name
- `fileSize: number` - File size in bytes
- `format: AudioFormat` - Audio format (WAV, MP3, M4A, FLAC)
- `sampleRate: number` - Sample rate in Hz (typically 16000 for Whisper)
- `channels: number` - Number of audio channels (1=mono, 2=stereo)
- `bitDepth: number | null` - Bit depth for uncompressed formats
- `duration: number` - Audio duration in seconds
- `quality: RecordingQuality` - Subjective quality assessment
- `source: RecordingSource` - Recording source (microphone, import, system audio)
- `encrypted: boolean` - Whether file is encrypted at rest
- `checksum: string` - File integrity checksum (SHA-256)
- `createdAt: DateTime` - Record creation timestamp

**Relationships**:
- Many-to-one with ConversationSession
- Referenced by Transcript (via sessionId)

**Validation Rules**:
- `filePath` must be valid and accessible local path
- `fileSize` must be positive integer
- `sampleRate` must be valid audio sample rate (8000-48000 Hz)
- `channels` must be 1 or 2
- `duration` must be positive number
- `checksum` must be valid SHA-256 hash

### Transcript

**Purpose**: Contains the transcribed text with speaker segments, timestamps, and confidence scores

**Attributes**:
- `id: string` - Unique transcript identifier (UUID)
- `sessionId: string` - Associated conversation session
- `text: string` - Complete transcript text
- `language: LanguageCode` - Detected/specified language (de, en, etc.)
- `confidence: number` - Overall transcription confidence score (0.0-1.0)
- `segments: TranscriptSegment[]` - Array of text segments with timing
- `editHistory: EditEvent[]` - Manual corrections and edit history
- `wordCount: number` - Total word count
- `speakerCount: number` - Number of identified speakers
- `processingTime: number` - Time taken for transcription in seconds
- `asrModel: string` - ASR model used (e.g., "whisper-large-v3")
- `status: TranscriptStatus` - Processing status
- `createdAt: DateTime` - Record creation timestamp
- `updatedAt: DateTime` - Last modification timestamp

**Complex Types**:
```typescript
interface TranscriptSegment {
  id: string;
  startTime: number;       // Start time in seconds
  endTime: number;         // End time in seconds
  text: string;            // Segment text
  speakerId: string;       // Associated speaker ID
  confidence: number;      // Segment confidence (0.0-1.0)
  words: WordTimestamp[];  // Word-level timestamps
}

interface WordTimestamp {
  word: string;
  startTime: number;
  endTime: number;
  confidence: number;
}

interface EditEvent {
  id: string;
  timestamp: DateTime;
  type: EditType;          // insert, delete, modify, speaker_change
  oldValue: string;
  newValue: string;
  position: number;        // Character position
  userId: string;          // Always "user" for single-user app
}
```

**Relationships**:
- Many-to-one with ConversationSession
- References AudioRecording (via sessionId)
- One-to-many with MarkerEvent

**Validation Rules**:
- `text` must be non-empty string
- `confidence` must be between 0.0 and 1.0
- `segments` must be chronologically ordered by startTime
- `speakerCount` must match unique speakers in segments
- All segment timings must be within audio duration

### SpeakerProfile

**Purpose**: Represents individual speakers with voice characteristics and manual labels

**Attributes**:
- `id: string` - Unique speaker identifier (UUID)
- `sessionId: string` - Associated conversation session
- `label: string` - User-assigned speaker label (e.g., "Therapist", "Client", "Speaker A")
- `role: SpeakerRole` - Professional role in conversation
- `voiceCharacteristics: VoiceProfile` - Technical voice analysis data
- `speakingTime: number` - Total speaking time in seconds
- `segmentCount: number` - Number of speaking segments
- `averageConfidence: number` - Average transcription confidence for this speaker
- `manualCorrections: number` - Count of manual speaker assignment corrections
- `isActive: boolean` - Whether speaker participated significantly
- `notes: string | null` - User notes about the speaker
- `createdAt: DateTime` - Record creation timestamp
- `updatedAt: DateTime` - Last modification timestamp

**Complex Types**:
```typescript
interface VoiceProfile {
  fundamentalFrequency: number | null;    // Average F0 in Hz
  spectralCentroid: number | null;        // Voice timbre characteristic
  energyLevel: number | null;             // Average volume level
  speakingRate: number | null;            // Words per minute
  pauseFrequency: number | null;          // Pauses per minute
  embeddings: number[] | null;            // Voice embedding vector (optional)
}
```

**Relationships**:
- Many-to-one with ConversationSession
- Referenced by TranscriptSegment (via speakerId)
- One-to-many with MarkerEvent

**Validation Rules**:
- `label` must be 1-50 characters
- `speakingTime` must be positive or zero
- `segmentCount` must be non-negative integer
- `averageConfidence` must be between 0.0 and 1.0
- `role` must be valid enum value

### MarkerEvent

**Purpose**: LD-3.4 marker detections (ATO/SEM/CLU/MEMA) with evidence and context

**Attributes**:
- `id: string` - Unique marker event identifier (UUID)
- `sessionId: string` - Associated conversation session
- `transcriptSegmentId: string` - Associated transcript segment
- `speakerId: string` - Speaker who triggered the marker
- `markerType: MarkerType` - LD-3.4 marker level (ATO, SEM, CLU, MEMA)
- `markerSubtype: string` - Specific marker rule name
- `confidence: number` - Detection confidence score (0.0-1.0)
- `startTime: number` - Start time in conversation (seconds)
- `endTime: number` - End time in conversation (seconds)
- `text: string` - Triggering text content
- `context: string` - Surrounding context text
- `rule: string` - Detection rule identifier
- `evidence: MarkerEvidence` - Evidence for marker detection
- `significance: SignificanceLevel` - Significance rating
- `verified: boolean` - Manual verification status
- `notes: string | null` - User annotations
- `createdAt: DateTime` - Record creation timestamp

**Complex Types**:
```typescript
interface MarkerEvidence {
  patterns: string[];           // Matched patterns
  keywords: string[];           // Trigger keywords
  linguisticFeatures: string[]; // Language features detected
  contextScore: number;         // Context relevance score
  precedingMarkers: string[];   // Related preceding markers
  explanation: string;          // Human-readable explanation
}
```

**Relationships**:
- Many-to-one with ConversationSession
- Many-to-one with TranscriptSegment
- Many-to-one with SpeakerProfile
- Referenced by RapportIndicator calculations

**Validation Rules**:
- `markerType` must be valid LD-3.4 level (ATO, SEM, CLU, MEMA)
- `confidence` must be between 0.0 and 1.0
- `startTime` and `endTime` must be within session duration
- `endTime` must be greater than `startTime`
- `text` must be non-empty string
- `rule` must reference valid marker detection rule

### RapportIndicator

**Purpose**: Calculated rapport and dialog dynamic indicators derived from marker patterns

**Attributes**:
- `id: string` - Unique indicator identifier (UUID)
- `sessionId: string` - Associated conversation session
- `timeWindow: TimeWindow` - Time period for calculation
- `indicatorType: IndicatorType` - Type of rapport indicator
- `value: number` - Calculated indicator value
- `scale: Scale` - Value scale information (min, max, interpretation)
- `trend: TrendDirection` - Trend direction (improving, declining, stable)
- `confidence: number` - Calculation confidence (0.0-1.0)
- `evidenceMarkers: string[]` - Contributing marker event IDs
- `calculation: CalculationDetails` - Calculation methodology and parameters
- `interpretation: string` - Human-readable interpretation
- `significance: SignificanceLevel` - Clinical/professional significance
- `validated: boolean` - Professional validation status
- `notes: string | null` - Professional annotations
- `createdAt: DateTime` - Record creation timestamp

**Complex Types**:
```typescript
interface TimeWindow {
  startTime: number;      // Window start (seconds)
  endTime: number;        // Window end (seconds)
  duration: number;       // Window duration (seconds)
}

interface Scale {
  minimum: number;        // Scale minimum value
  maximum: number;        // Scale maximum value
  unit: string;           // Unit of measurement
  interpretation: string; // Scale interpretation guide
}

interface CalculationDetails {
  algorithm: string;      // Calculation algorithm name
  parameters: object;     // Algorithm parameters
  weightings: object;     // Marker weightings used
  baseline: number | null; // Baseline comparison value
}
```

**Relationships**:
- Many-to-one with ConversationSession
- References multiple MarkerEvent (via evidenceMarkers)

**Validation Rules**:
- `value` must be within `scale.minimum` and `scale.maximum`
- `confidence` must be between 0.0 and 1.0
- `timeWindow.endTime` must be greater than `timeWindow.startTime`
- `evidenceMarkers` must reference valid MarkerEvent IDs
- `calculation.algorithm` must be recognized algorithm

### AnalysisReport

**Purpose**: Generated comprehensive report containing session summary, insights, and export data

**Attributes**:
- `id: string` - Unique report identifier (UUID)
- `sessionId: string` - Associated conversation session
- `reportType: ReportType` - Type of report (summary, detailed, executive)
- `template: string` - Report template identifier
- `generatedAt: DateTime` - Report generation timestamp
- `summary: SessionSummary` - Key session insights
- `statistics: SessionStatistics` - Quantitative session data
- `insights: Insight[]` - Professional insights and observations
- `recommendations: Recommendation[]` - Professional recommendations
- `exportFormats: ExportFormat[]` - Available export formats
- `confidentiality: ConfidentialityLevel` - Report confidentiality level
- `validatedBy: string | null` - Professional who validated report
- `validatedAt: DateTime | null` - Validation timestamp
- `version: number` - Report version number
- `status: ReportStatus` - Report generation status

**Complex Types**:
```typescript
interface SessionSummary {
  duration: number;              // Total session duration
  speakerBreakdown: SpeakerStats[]; // Speaking time per speaker
  markerCounts: MarkerCounts;    // Marker occurrences by type
  rapportTrend: TrendAnalysis;   // Overall rapport progression
  keyMoments: KeyMoment[];       // Significant conversation moments
  overallAssessment: string;     // Professional assessment summary
}

interface SessionStatistics {
  wordCount: number;
  averageSegmentLength: number;
  speakerTurnRate: number;
  silenceDuration: number;
  overlapDuration: number;
  transcriptionAccuracy: number;
}

interface Insight {
  id: string;
  category: InsightCategory;     // communication, rapport, dynamics, concerns
  title: string;
  description: string;
  evidence: string[];            // Supporting evidence
  significance: SignificanceLevel;
  timeReferences: number[];      // Reference timestamps
}

interface Recommendation {
  id: string;
  category: RecommendationCategory; // follow_up, technique, attention
  title: string;
  description: string;
  priority: Priority;
  actionable: boolean;
  evidence: string[];
}
```

**Relationships**:
- One-to-one with ConversationSession
- References MarkerEvent and RapportIndicator for insights

**Validation Rules**:
- `reportType` must be valid enum value
- `generatedAt` cannot be in the future
- `version` must be positive integer
- `summary.duration` must match session duration
- All referenced timestamps must be within session timeframe

## Supporting Types

### Enums

```typescript
enum SessionType {
  THERAPY = 'therapy',
  LEGAL = 'legal',
  CONSULTATION = 'consultation',
  COACHING = 'coaching',
  MEDIATION = 'mediation',
  OTHER = 'other'
}

enum SessionStatus {
  CREATED = 'created',
  RECORDING = 'recording',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  FAILED = 'failed',
  ARCHIVED = 'archived'
}

enum PrivacyLevel {
  STANDARD = 'standard',
  CONFIDENTIAL = 'confidential',
  PRIVILEGED = 'privileged',
  TOP_SECRET = 'top_secret'
}

enum AudioFormat {
  WAV = 'wav',
  MP3 = 'mp3',
  M4A = 'm4a',
  FLAC = 'flac',
  OGG = 'ogg'
}

enum RecordingQuality {
  POOR = 'poor',
  FAIR = 'fair',
  GOOD = 'good',
  EXCELLENT = 'excellent'
}

enum RecordingSource {
  MICROPHONE = 'microphone',
  SYSTEM_AUDIO = 'system_audio',
  IMPORTED_FILE = 'imported_file',
  MIXED = 'mixed'
}

enum TranscriptStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  EDITED = 'edited'
}

enum EditType {
  INSERT = 'insert',
  DELETE = 'delete',
  MODIFY = 'modify',
  SPEAKER_CHANGE = 'speaker_change'
}

enum SpeakerRole {
  PROFESSIONAL = 'professional',    // Therapist, lawyer, consultant
  CLIENT = 'client',                // Patient, client, customer
  OTHER = 'other',                  // Additional participants
  UNKNOWN = 'unknown'               // Unidentified speakers
}

enum MarkerType {
  ATO = 'ATO',    // Aufmerksamkeits-Marker
  SEM = 'SEM',    // Semantik-Marker
  CLU = 'CLU',    // Cluster-Marker
  MEMA = 'MEMA'   // Memorisierung-Marker
}

enum SignificanceLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

enum IndicatorType {
  RAPPORT_LEVEL = 'rapport_level',
  COMMUNICATION_FLOW = 'communication_flow',
  EMOTIONAL_TONE = 'emotional_tone',
  ENGAGEMENT_LEVEL = 'engagement_level',
  RESISTANCE = 'resistance',
  COOPERATION = 'cooperation',
  TRUST_BUILDING = 'trust_building'
}

enum TrendDirection {
  IMPROVING = 'improving',
  DECLINING = 'declining',
  STABLE = 'stable',
  FLUCTUATING = 'fluctuating'
}

enum ReportType {
  SUMMARY = 'summary',
  DETAILED = 'detailed',
  EXECUTIVE = 'executive',
  TECHNICAL = 'technical'
}

enum ConfidentialityLevel {
  PUBLIC = 'public',
  INTERNAL = 'internal',
  CONFIDENTIAL = 'confidential',
  PRIVILEGED = 'privileged'
}

enum ReportStatus {
  GENERATING = 'generating',
  READY = 'ready',
  FAILED = 'failed',
  VALIDATED = 'validated'
}
```

## Data Flow Patterns

### Session Workflow
1. User creates ConversationSession with metadata and consent
2. AudioRecording captures live audio or imports existing file
3. Transcript generation via WhisperX (ASR + diarization)
4. SpeakerProfile creation and manual correction support
5. MarkerEvent detection via LD-3.4 pipeline integration
6. RapportIndicator calculation from marker patterns
7. AnalysisReport generation with professional insights

### Real-time Analysis
1. Audio segments processed in near real-time during recording
2. Transcript segments generated with word-level timestamps
3. Marker detection triggers immediately on segment completion
4. Rapport indicators updated in sliding time windows
5. UI updates streamed via WebSocket-style messaging

### Professional Review
1. Session completion triggers comprehensive analysis
2. Manual review and correction of speaker assignments
3. Marker verification and professional annotations
4. Report generation with customizable templates
5. Export to professional formats (PDF, structured data)

## Storage Strategy

### SQLCipher Database Tables
- **sessions**: ConversationSession metadata
- **audio_recordings**: AudioRecording file information
- **transcripts**: Transcript text and segments
- **speakers**: SpeakerProfile data and characteristics
- **markers**: MarkerEvent detections and evidence
- **indicators**: RapportIndicator calculations
- **reports**: AnalysisReport metadata and content

### File System Storage
- **Audio files**: Encrypted local storage with OS-level encryption
- **Report exports**: PDF, CSV, JSON files in user-specified locations
- **Model files**: Whisper models cached locally for offline operation
- **Backups**: Encrypted session backups for data protection

### Data Retention
- ConversationSessions: User-controlled retention (default: indefinite)
- AudioRecordings: Configurable auto-deletion (default: 1 year)
- Transcripts: Persist with sessions for searchability
- MarkerEvents: Persist for longitudinal analysis
- AnalysisReports: User-controlled archival and deletion

## Performance Considerations

### Scalability Targets
- Max 1000 conversation sessions per user
- Max 10,000 marker events per session
- Max 100MB audio files (2+ hours at CD quality)
- Max 50,000 words per transcript

### Optimization Strategies
- Indexed full-text search on transcript text
- Lazy loading of audio file metadata
- Cached marker detection models
- Incremental marker analysis during transcription
- Background report generation
- Compressed storage for historical data

---

**Data Model Status**: Complete  
**Entity Count**: 7 core entities + 15 supporting enums  
**Validation Rules**: Comprehensive business logic defined  
**Ready for**: API contract generation and implementation