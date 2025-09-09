# TransRapport v0.1.0-pilot Quickstart Guide

🏛️ **Constitutional Analysis Framework: LD-3.4**  
🔒 **Privacy-First Offline Operation**  
📋 **Production Ready Pilot Release**

## ⚡ Quick Start (5 minutes)

### 1. Installation

```bash
# Download and extract
tar -xzf transrapport-0.1.0-pilot-src.tar.gz
cd transrapport-0.1.0-pilot

# Test CLI
python3 me.py status
```

### 2. Desktop UI (Offline)

```bash
# Build UI (one-time)
cd desktop
npm install
npm run build

# UI is bundled - no servers needed
# Launch via system file manager: open desktop/dist/index.html
```

### 3. Basic Workflow

```bash
# Step 1: Start recording
python3 me.py audio start --conv "demo-session" --device default

# Step 2: Stop recording (after speaking)
python3 me.py audio stop --conv "demo-session"

# Step 3: Transcribe
python3 me.py transcribe transcribe --conv "demo-session" --output-json

# Step 4: Diarize (speaker separation)
python3 me.py diarize diarize --conv "demo-session" --output-json

# Step 5: Constitutional Analysis (LD-3.4)
python3 me.py run scan --conv "demo-session"

# Step 6: View markers
python3 me.py view events --conv "demo-session" --level ato --output-json
python3 me.py view events --conv "demo-session" --level sem --output-json

# Step 7: Export
python3 me.py export report --conv "demo-session" --format pdf
```

## 📊 Constitutional Markers (LD-3.4)

TransRapport v0.1.0-pilot includes **frozen** constitutional markers:

### ATO (Autonomy)
- `question_open` - Open-ended questions
- `choice_offering` - Offering choices/options
- `permission_seeking` - Seeking permission

### SEM (Semantic Understanding)
- `empathy_expression` - Expressing empathy
- `validation` - Validating understanding
- `understanding_check` - Checking comprehension

### CLU (Clustering/Connection)
- `shared_experience` - References to shared experiences
- `similarity_acknowledgment` - Acknowledging similarities
- `group_identity` - Building group identity

### MEMA (Memory/Mental Models)
- `reference_recall` - Recalling previous context
- `context_building` - Building situational context
- `assumption_check` - Checking assumptions

## 🎯 Analysis Windows (FROZEN v0.1.0)

- **SEM Window**: `"ANY 2 IN 3"` - Any 2 semantic markers within 3 segments
- **CLU Window**: `"AT_LEAST 1 IN 5"` - At least 1 clustering marker within 5 segments
- **Confidence Threshold**: `0.75` (75%)
- **Min Duration**: `1.5 seconds`

## 🖥️ Desktop UI Features

- ✅ **Offline Only** - No network connections
- ✅ **Real-time Progress** - Live transcription/analysis updates
- ✅ **Session Management** - Track multiple conversations
- ✅ **Constitutional Markers** - View ATO, SEM, CLU, MEMA events
- ✅ **Export Tools** - PDF reports, CSV data
- ✅ **Audio Devices** - Multiple input source support

## 🔧 System Requirements

### Minimum
- Python 3.11+ 
- Node.js 18+ (for UI build)
- 4GB RAM
- 2GB storage

### Recommended
- Python 3.12
- 8GB RAM
- Audio input device
- Linux/Ubuntu (primary platform)

## 🚨 Important Notes

### v0.1.0-pilot Limitations
- **Mock Analysis**: Uses demonstration data, not full AI analysis
- **No Network**: Completely offline - no cloud services
- **Linux Focus**: Primary development on Linux platform
- **Frozen Config**: All settings locked for stability

### Data Privacy
- ✅ All processing happens locally
- ✅ No data transmission
- ✅ No cloud dependencies
- ✅ User controls all files

## 📁 File Structure

```
sessions/[conversation-id]/
├── raw.wav              # Original recording
├── transcript.json      # Whisper transcription
├── diarization.json     # Speaker separation
├── analysis.json        # LD-3.4 constitutional markers
└── events/
    ├── ato.json        # Autonomy markers
    ├── sem.json        # Semantic markers
    ├── clu.json        # Clustering markers
    └── mema.json       # Memory markers
```

## 🆘 Troubleshooting

### Audio Issues
```bash
# List available devices
python3 me.py audio devices

# Test with specific device
python3 me.py audio start --device "USB Microphone"
```

### UI Issues
```bash
# Rebuild UI
cd desktop
npm run build

# Check bundled assets
ls -la desktop/dist/
```

### Permission Issues
```bash
chmod +x me.py
python3 me.py status
```

## 🔄 Next Steps

1. **Test the workflow** with demo data
2. **Record real conversations** (with consent)
3. **Analyze constitutional patterns**
4. **Export professional reports**
5. **Review privacy compliance**

---

**TransRapport v0.1.0-pilot** | Constitutional Framework: **LD-3.4** | **Offline & Private**