# TransRapport Hybrid Architecture - Technical Specification

## Core Architecture Overview

### Technology Stack
- **Frontend**: SvelteKit 2.0 + TypeScript 5.2 + Tailwind CSS 3.4
- **Desktop Runtime**: Tauri 2.0 (Rust 1.75 + WebView)
- **Backend Engine**: Python 3.12 Sidecar Process
- **IPC**: WebSocket (primary) + CLI Pipes (fallback)
- **Storage**: SQLite 3.44 + File System
- **Serialization**: MessagePack 1.0 + NDJSON

### Component Architecture

#### 1. Frontend Layer (SvelteKit)
```
src/
├── app.html                    # Main HTML template
├── app.d.ts                    # TypeScript definitions
├── lib/
│   ├── stores/                 # Svelte stores for state
│   │   ├── session.ts          # Session management
│   │   ├── audio.ts            # Audio device state
│   │   ├── markers.ts          # Marker data
│   │   └── config.ts           # Configuration state
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   ├── capture/            # Capture mode components
│   │   ├── explore/            # Explore mode components
│   │   └── perform/            # Perform mode components
│   ├── services/
│   │   ├── ipc.ts              # IPC communication
│   │   ├── websocket.ts        # WebSocket client
│   │   ├── cli.ts              # CLI fallback
│   │   └── validation.ts       # Schema validation
│   └── utils/
│       ├── audio.ts            # Audio utilities
│       ├── config.ts           # Config management
│       └── metrics.ts          # Performance metrics
├── routes/
│   ├── +page.svelte            # Main application
│   ├── capture/+page.svelte    # Capture mode
│   ├── explore/+page.svelte    # Explore mode
│   └── perform/+page.svelte    # Perform mode
└── hooks.client.ts             # Client-side hooks
```

#### 2. Tauri Layer (Rust)
```
src-tauri/
├── src/
│   ├── main.rs                 # Application entry point
│   ├── app.rs                  # App state management
│   ├── ipc.rs                  # IPC handlers
│   ├── websocket.rs            # WebSocket server
│   ├── cli.rs                  # CLI pipe handlers
│   ├── python.rs               # Python sidecar management
│   ├── storage.rs              # SQLite operations
│   └── audio.rs                # Audio device handling
├── Cargo.toml                  # Rust dependencies
└── tauri.conf.json             # Tauri configuration
```

#### 3. Python Engine Layer
```
engine/
├── __init__.py                # Engine package
├── core/
│   ├── prosody.py             # Prosody analysis (16kHz, 25/10ms)
│   ├── markers.py             # Marker detection & scoring
│   ├── ewma.py                # EWMA filtering & homeostasis
│   └── uncertainty.py         # Uncertainty quantification
├── models/
│   ├── whisper.py             # Optional STT integration
│   ├── pyannote.py            # Optional diarization
│   └── embeddings.py          # Optional speaker embeddings
├── config/
│   ├── prosody.json           # Prosody thresholds
│   ├── markers.yaml           # Marker definitions
│   ├── weights.yaml           # Scoring weights
│   └── schemas/               # JSON schemas for validation
├── services/
│   ├── websocket_server.py   # WebSocket event streaming
│   ├── cli_interface.py       # CLI command processing
│   └── audio_processor.py     # Audio I/O handling
└── main.py                    # Engine entry point
```

### Data Flow Architecture

#### Live Processing Pipeline
```
Audio Input → Ring Buffer → Prosody Analysis → Marker Candidates → EWMA Filtering → Confirmed Markers → UI Update
     ↓             ↓              ↓                    ↓                  ↓                    ↓            ↓
  16kHz       25/10ms        f0, RMS,           Pattern              Stabilize          Validate      Display
  WAV         Frames         Pause, Rate       Matching            Confidence         Thresholds    Overlays
```

#### Configuration Flow
```
YAML Config → Schema Validation → Dry Run Check → Hot Reload → Engine Update → UI Feedback
     ↓              ↓                    ↓              ↓              ↓              ↓
  prosody.json   JSON Schema         Test Run      WebSocket       Parameter        Success/Error
  markers.yaml   Validation         No Audio      Update          Application     Notification
  weights.yaml   Error Check        Processing    Confirmation    Confirmation
```

### IPC Protocol Specification

#### WebSocket Events (Primary)
```typescript
// Outgoing Events (Engine → UI)
interface ProsodyEvent {
  type: 'prosody';
  timestamp: number;
  f0: number;
  rms: number;
  pause_ms: number;
  rate_wpm: number;
}

interface MarkerEvent {
  type: 'marker';
  timestamp: number;
  marker_id: string;
  confidence: number;
  window: string; // "3/5" format
  evidence: string;
}

// Incoming Commands (UI → Engine)
interface ConfigUpdate {
  type: 'config_update';
  config_type: 'prosody' | 'markers' | 'weights';
  data: any;
  dry_run: boolean;
}
```

#### CLI Fallback Protocol
```bash
# Commands
./engine --config-update prosody --data '{"f0_min": 80}' --dry-run
./engine --start-capture --device "default" --format wav
./engine --get-markers --level ato --last 200 --format json
```

### Storage Architecture

#### SQLite Schema
```sql
-- Sessions table
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  status TEXT CHECK(status IN ('idle', 'recording', 'processing', 'completed')),
  duration REAL,
  config_hash TEXT
);

-- Audio segments
CREATE TABLE audio_segments (
  id TEXT PRIMARY KEY,
  session_id TEXT REFERENCES sessions(id),
  start_time REAL,
  end_time REAL,
  file_path TEXT,
  format TEXT DEFAULT 'wav'
);

-- Markers
CREATE TABLE markers (
  id TEXT PRIMARY KEY,
  session_id TEXT REFERENCES sessions(id),
  timestamp REAL,
  marker_type TEXT,
  marker_subtype TEXT,
  confidence REAL,
  window TEXT,
  evidence TEXT
);

-- Configurations
CREATE TABLE configurations (
  id TEXT PRIMARY KEY,
  session_id TEXT REFERENCES sessions(id),
  config_type TEXT,
  config_data TEXT,
  hash TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Performance Targets

#### Latency Budget (p95)
- Audio Capture: 5ms
- Prosody Analysis: 25ms (16kHz, 25ms frames)
- Marker Detection: 15ms
- IPC Transport: 10ms (WebSocket) / 30ms (CLI)
- UI Rendering: 10ms
- **Total: ≤75ms** (Ziel: ≤150ms)

#### Resource Budget
- CPU: ≤45% (Ziel: ≤60%)
- RAM: ≤350MB (Ziel: ≤500MB)
- Storage: ≤50MB base + audio (Ziel: ≤80MB)
- Startup: ≤1.2s (Ziel: ≤2s)

### Error Handling & Recovery

#### Graceful Degradation
1. **WebSocket Failure** → Automatic fallback to CLI pipes
2. **Python Engine Crash** → Automatic restart with last config
3. **Audio Device Loss** → Device selection dialog + recovery
4. **Config Validation Error** → Rollback to last valid config
5. **Storage Corruption** → Automatic repair or fresh start

#### Monitoring & Telemetry
- Local performance metrics (no network required)
- Error logs with automatic rotation
- Session recovery checkpoints
- Configuration change history

### Security Model

#### Offline-First Security
- No network dependencies
- Local data encryption (SQLite + file encryption)
- Secure IPC between processes
- Input validation at all boundaries
- Safe audio device access

#### Configuration Security
- Schema-validated configurations
- Dry-run validation before application
- Configuration rollback capability
- Hash-based integrity checking
