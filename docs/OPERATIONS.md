# TransRapport v0.1.0-pilot Operations Guide

🏛️ **Constitutional Framework: LD-3.4**  
⚙️ **Production Operations**  
🔒 **Offline-Only Deployment**

## 🚀 Deployment Guide

### System Requirements

#### Minimum Specifications
```
OS: Linux (Ubuntu 20.04+ recommended)
CPU: 2 cores, 2.0GHz
RAM: 4GB
Storage: 2GB available
Python: 3.11+
Node.js: 18+ (for UI builds)
```

#### Recommended Specifications  
```
OS: Ubuntu 22.04 LTS
CPU: 4 cores, 3.0GHz
RAM: 8GB
Storage: 10GB available (for audio sessions)
Python: 3.12
Audio: Dedicated microphone input
```

### Installation Steps

#### 1. System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nodejs npm

# Verify versions
python3 --version  # Should be 3.11+
node --version     # Should be 18+
```

#### 2. Application Installation
```bash
# Download and extract
tar -xzf transrapport-0.1.0-pilot-src.tar.gz
cd transrapport-0.1.0-pilot

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt || echo "Installing minimal dependencies"
pip install numpy scipy scikit-learn librosa || echo "Optional ML dependencies"
```

#### 3. UI Build (One-time)
```bash
# Build desktop interface
cd desktop
npm install
npm run build
cd ..

# Verify build
ls -la desktop/dist/
```

#### 4. System Test
```bash
# Test CLI
python3 me.py status

# Test UI integration
node test-ui-wiring.js

# Verify offline operation
ss -tulpn | grep -E ":(80|443|8080|3000|5173)" # Should be empty
```

## 🔧 Configuration Management

### Core Configuration (FROZEN v0.1.0)
```python
# src/config/v0_1_0_defaults.py - DO NOT MODIFY
V0_1_0_DEFAULTS = {
    "VERSION": "0.1.0-pilot",
    "CONSTITUTIONAL_FRAMEWORK": "LD-3.4",
    "CONFIDENCE_THRESHOLD": 0.75,
    "DEFAULT_WINDOW_SEM": "ANY 2 IN 3",
    "DEFAULT_WINDOW_CLU": "AT_LEAST 1 IN 5",
    # ... other frozen settings
}
```

### Environment Variables
```bash
# Optional environment configuration
export TRANSRAPPORT_LOG_LEVEL=INFO
export TRANSRAPPORT_DATABASE_PATH=/data/transrapport.db
export TRANSRAPPORT_EXPORT_DIR=/exports
export TRANSRAPPORT_TEMP_DIR=/tmp/transrapport
```

### File System Structure
```
transrapport-0.1.0-pilot/
├── me.py                    # CLI entry point
├── src/                     # Core application
├── desktop/                 # UI components
│   └── dist/               # Built UI assets (offline)
├── data/                   # Database storage
├── sessions/               # Recording sessions
├── exports/                # Generated reports
├── temp/                   # Temporary processing
└── tests/                  # Golden tests
```

## 📊 Monitoring & Logging

### Log Management
```bash
# View real-time logs
tail -f transrapport.log

# Log rotation (manual)
logrotate -f logrotate.conf

# Check log levels
grep -i error transrapport.log
grep -i warning transrapport.log
```

### Health Checks
```bash
# System health script
#!/bin/bash
echo "🔍 TransRapport Health Check"

# 1. CLI responsiveness
python3 me.py status > /dev/null && echo "✅ CLI operational" || echo "❌ CLI issues"

# 2. Database accessibility  
test -f data/transrapport.db && echo "✅ Database exists" || echo "❌ Database missing"

# 3. UI assets
test -f desktop/dist/index.html && echo "✅ UI built" || echo "❌ UI missing"

# 4. No network connections
! ss -tulpn | grep -E ":(80|443|8080|3000|5173)" && echo "✅ Offline confirmed" || echo "❌ Network detected"

# 5. Golden test compliance
python3 tests/test_goldens.py && echo "✅ Golden tests pass" || echo "❌ Golden tests fail"
```

### Performance Monitoring
```bash
# Resource usage
ps aux | grep transrapport
df -h | grep -E "(data|sessions|exports)"

# Session analysis
find sessions/ -name "*.json" | wc -l  # Number of processed sessions
du -sh sessions/                       # Storage usage
```

## 🔄 Maintenance Procedures

### Daily Operations
```bash
# 1. Health check
./scripts/health-check.sh

# 2. Clear temporary files
find temp/ -type f -mtime +1 -delete

# 3. Log rotation
logrotate -f logrotate.conf

# 4. Backup check
rsync -av data/ /backup/transrapport-data/
```

### Weekly Maintenance
```bash
# 1. Full system test
python3 tests/test_goldens.py

# 2. Session cleanup (if needed)
find sessions/ -type d -empty -mtime +30 -delete

# 3. Database maintenance
echo "VACUUM;" | sqlite3 data/transrapport.db

# 4. Update verification
git tag | grep v0.1.0-pilot # Verify version
```

### Monthly Reviews
- Review storage usage trends
- Analyze error patterns in logs
- Update system dependencies (carefully)
- Test backup/restore procedures
- Review security posture

## 📋 Backup & Recovery

### Data Backup Strategy
```bash
# Critical data locations
BACKUP_DIRS=(
    "data/"           # Database
    "sessions/"       # Audio and analysis
    "exports/"        # Generated reports
)

# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_ROOT="/backup/transrapport"

for dir in "${BACKUP_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        rsync -av "$dir" "$BACKUP_ROOT/$DATE/"
    fi
done

# Compress daily backup
tar -czf "$BACKUP_ROOT/transrapport-$DATE.tar.gz" "$BACKUP_ROOT/$DATE/"
```

### Recovery Procedures
```bash
# 1. System restoration
tar -xzf transrapport-YYYYMMDD.tar.gz
cp -r backup/data/ ./
cp -r backup/sessions/ ./

# 2. Database recovery
sqlite3 data/transrapport.db ".schema" # Verify structure
sqlite3 data/transrapport.db "SELECT COUNT(*) FROM sessions;"

# 3. UI rebuild
cd desktop && npm run build
```

## 🚨 Incident Response

### Common Issues

#### CLI Not Responding
```bash
# Diagnosis
python3 me.py status
echo $?  # Exit code

# Resolution
ps aux | grep python3  # Check for hung processes
kill -9 [PID]          # If needed
```

#### UI Assets Missing
```bash
# Diagnosis
ls -la desktop/dist/

# Resolution
cd desktop
npm install
npm run build
```

#### Database Corruption
```bash
# Diagnosis
sqlite3 data/transrapport.db "PRAGMA integrity_check;"

# Recovery
cp data/transrapport.db data/transrapport.db.backup
sqlite3 data/transrapport.db "VACUUM;"
```

#### Storage Full
```bash
# Diagnosis
df -h

# Cleanup
find temp/ -type f -delete
find sessions/ -name "raw.wav" -mtime +30 -delete  # Old audio files
```

### Emergency Procedures

#### Complete System Reset
```bash
# 1. Backup critical data
cp -r sessions/ /emergency-backup/
cp data/transrapport.db /emergency-backup/

# 2. Clean installation
rm -rf .venv/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Rebuild UI
cd desktop && rm -rf node_modules/ dist/
npm install && npm run build

# 4. Restore data
cp /emergency-backup/transrapport.db data/
cp -r /emergency-backup/sessions/ ./
```

## 🔐 Security Operations

### Security Monitoring
```bash
# Network isolation verification
ss -tulpn | grep python3  # Should be empty
netstat -an | grep LISTEN  # Check for listeners

# File permission audit
find . -type f -perm /002 -exec ls -la {} \;  # World-writable files
find sessions/ -type f ! -perm 600 -exec chmod 600 {} \;
```

### Access Control
```bash
# Secure installation
chmod 700 .                    # Application directory
chmod 600 data/transrapport.db # Database
chmod -R 700 sessions/         # Session data
chmod -R 755 desktop/dist/     # UI assets (read-only)
```

### Compliance Verification
```bash
# GDPR compliance check
find . -name "*.json" -exec grep -l "personal" {} \;  # Should be empty
find . -name "*.log" -exec grep -l "email\|phone" {} \;  # Check logs

# Constitutional framework verification
python3 -c "
from src.config.v0_1_0_defaults import get_v010_config
config = get_v010_config()
assert config.get_version() == '0.1.0-pilot'
assert 'LD-3.4' in str(config.constitutional_framework)
print('✅ Constitutional compliance verified')
"
```

## 🔄 Update Procedures

### Version Control
```bash
# Current version verification
git tag | grep v0.1.0-pilot
python3 me.py status | grep "v0.1.0-pilot"

# No updates allowed for frozen pilot
echo "⚠️  v0.1.0-pilot is frozen - no updates permitted"
```

### Future Update Preparation
- Document current configuration
- Backup all data before any future updates
- Test updates in isolated environment
- Verify constitutional framework compatibility

## 📞 Support & Contact

### Self-Service Diagnostics
1. Run health check script
2. Check golden tests: `python3 tests/test_goldens.py`
3. Verify offline operation: No network connections
4. Review logs for error patterns

### Documentation References
- `docs/QUICKSTART.md` - Basic usage
- `docs/SECURITY.md` - Security architecture
- `docs/SCHEMA.md` - Data formats
- `docs/OPERATIONS.md` - This guide

### Issue Escalation
- **Configuration Issues**: Check frozen defaults
- **Performance Issues**: Monitor resource usage
- **Security Concerns**: Follow incident response
- **Data Issues**: Verify backup integrity

---

**TransRapport v0.1.0-pilot is designed for stable, offline operation. All procedures prioritize data privacy and system security.**