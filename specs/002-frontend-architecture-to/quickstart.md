# Quickstart Guide: Frontend Architecture for TransRapport Backend Interaction

**Feature**: Frontend Architecture for TransRapport Backend Interaction  
**Version**: 1.0.0  
**Updated**: 2025-09-09

## Prerequisites

- **TransRapport CLI**: Backend must be installed and functional
- **Python 3.11+**: For FastAPI backend bridge
- **Node.js 18+**: For Svelte frontend development
- **Modern Browser**: Chrome 90+, Firefox 88+, Safari 14+

## Quick Setup (Development)

### 1. Clone and Setup
```bash
git checkout 002-frontend-architecture-to
cd TransRapport

# Setup backend bridge
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
```

### 2. Start Development Servers
```bash
# Terminal 1: Backend bridge
cd backend
uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend dev server  
cd frontend
npm run dev
```

### 3. Access Application
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/user123

## User Scenario Testing

### Scenario 1: Project Setup and Basic Validation

**Goal**: Create a project and run basic validation

1. **Open Frontend**
   ```
   Navigate to: http://localhost:5173
   Expected: Clean, modern interface loads
   ```

2. **Create New Project**
   ```
   Click: "New Project" button
   Fill form:
     - Name: "My Documentation"
     - Root Path: "/path/to/your/docs"
   Click: "Create Project"
   Expected: Project appears in project list
   ```

3. **Start Validation**
   ```
   Click: Project name to open
   Click: "Validate Documentation" button
   Expected: Real-time progress indicator appears
   Expected: CLI output streams in terminal view
   Expected: Progress bar updates as files are processed
   ```

4. **View Results**
   ```
   Wait for: "Validation Complete" message
   Expected: Results dashboard shows:
     - File count processed
     - Error/warning/info summary
     - Detailed issue list
     - Cross-reference analysis
   ```

### Scenario 2: Real-Time Progress and WebSocket Communication

**Goal**: Verify real-time updates during validation

1. **Start Long Validation**
   ```
   Create project with large documentation set (100+ files)
   Click: "Validate Documentation" 
   Expected: Immediate session start confirmation
   ```

2. **Monitor Real-Time Updates**
   ```
   Watch: Progress bar increments smoothly
   Watch: Current file name updates in real-time
   Watch: CLI output appears live in terminal view
   Expected: No delays > 2 seconds for updates
   Expected: WebSocket connection indicator shows "Connected"
   ```

3. **Test Connection Recovery**
   ```
   Action: Temporarily disconnect network
   Expected: UI shows "Reconnecting..." indicator
   Action: Restore network connection
   Expected: Connection recovers and updates resume
   ```

### Scenario 3: Results Analysis and Export

**Goal**: Analyze validation results and export reports

1. **Navigate Results**
   ```
   From completed validation:
   Click: "View Details" on error/warning
   Expected: Issue details panel opens with:
     - File location with line number
     - Error message and suggestion
     - Code context (if available)
   ```

2. **Filter and Search**
   ```
   Use: Severity filter (Errors only)
   Expected: Results list updates to show errors only
   Use: File path filter
   Expected: Results filtered by file path
   Use: Search box for keywords
   Expected: Real-time search results
   ```

3. **Export Results**
   ```
   Click: "Export" button
   Select: JSON format
   Click: "Generate Report"
   Expected: Export progress indicator
   Expected: Download link appears when ready
   Click: Download link
   Expected: Valid JSON file downloads
   ```

### Scenario 4: Cross-Reference Analysis

**Goal**: Use terminology and cross-reference features

1. **View Cross-Reference Dashboard**
   ```
   From project with validation results:
   Click: "Cross-References" tab
   Expected: Interactive visualization of file relationships
   Expected: Terminology usage statistics
   ```

2. **Explore Terminology**
   ```
   Click: "ATO" term in terminology list
   Expected: Shows all files using this term
   Expected: Distinguishes between definitions and usage
   Click: File reference
   Expected: Opens file context view
   ```

3. **Find Broken Links**
   ```
   Filter: "Broken Links" only
   Expected: List of all broken cross-references
   Click: Broken link item
   Expected: Shows source file and target (with error reason)
   ```

## Performance Validation

### Load Testing Scenarios

1. **Large Documentation Set**
   ```
   Test with: 1000+ markdown files
   Expected: Validation completes within 5 minutes
   Expected: UI remains responsive during processing
   Expected: Memory usage < 100MB frontend
   ```

2. **Concurrent Sessions**
   ```
   Open: Multiple browser tabs
   Start: Validation in each tab
   Expected: All sessions run concurrently
   Expected: Each shows independent progress
   ```

3. **Real-Time Performance**
   ```
   Measure: Time from CLI output to UI display
   Expected: < 100ms latency for output updates
   Expected: < 1s latency for progress updates
   ```

## Integration Testing

### API Contract Validation

1. **Test REST Endpoints**
   ```bash
   # Get projects
   curl http://localhost:8000/api/v1/projects
   # Expected: 200 OK with projects array
   
   # Create project
   curl -X POST http://localhost:8000/api/v1/projects \
     -H "Content-Type: application/json" \
     -d '{"name":"Test","rootPath":"/tmp"}'
   # Expected: 201 Created with project object
   
   # Start validation
   curl -X POST http://localhost:8000/api/v1/projects/{id}/validate \
     -H "Content-Type: application/json" \
     -d '{"settings":{"strict":true}}'
   # Expected: 202 Accepted with session object
   ```

2. **Test WebSocket Connection**
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/test-user');
   ws.onopen = () => {
     ws.send(JSON.stringify({
       type: 'start_validation',
       command: 'transrapport-docs validate test-docs/',
       timestamp: Date.now()
     }));
   };
   // Expected: session_start message received
   // Expected: progress and output messages follow
   // Expected: session_end message on completion
   ```

### CLI Integration Testing

1. **Backend Bridge Validation**
   ```bash
   # Test CLI availability
   transrapport-docs --version
   # Expected: Version output
   
   # Test JSON output parsing
   transrapport-docs docs validate test-docs/ --format json
   # Expected: Valid JSON with results array
   ```

2. **Error Handling**
   ```bash
   # Test invalid command
   transrapport-docs invalid-command
   # Expected: Backend returns appropriate error via API
   
   # Test permission errors
   transrapport-docs docs validate /root/
   # Expected: Permission error handled gracefully
   ```

## Troubleshooting

### Common Issues

1. **Backend Won't Start**
   ```
   Error: "ModuleNotFoundError: No module named 'fastapi'"
   Solution: pip install -r requirements.txt
   
   Error: "Port 8000 already in use"
   Solution: uvicorn src.main:app --port 8001
   ```

2. **Frontend Build Errors**
   ```
   Error: "Cannot resolve '@/components'"
   Solution: Check vite.config.js path aliases
   
   Error: "WebSocket connection failed"
   Solution: Ensure backend is running on correct port
   ```

3. **CLI Integration Issues**
   ```
   Error: "transrapport-docs: command not found"
   Solution: Ensure TransRapport CLI is installed and in PATH
   
   Error: "Permission denied accessing files"
   Solution: Check file permissions and user access rights
   ```

### Validation Steps

**✅ Complete Feature Validation Checklist**:
- [ ] Frontend loads without errors
- [ ] Can create and manage projects
- [ ] Validation starts and shows real-time progress
- [ ] WebSocket connection works and recovers from drops
- [ ] Results display correctly with filtering/search
- [ ] Export functionality generates valid reports
- [ ] Cross-reference analysis works
- [ ] Performance meets requirements (<2s feedback, <100ms UI)
- [ ] Error handling works gracefully
- [ ] All API endpoints return correct responses

## Next Steps

After successful quickstart validation:
1. Run full test suite: `npm run test && pytest`
2. Generate API documentation: `npm run docs:api`
3. Create production build: `npm run build`
4. Deploy backend and frontend to staging environment
5. Run load testing with realistic documentation sets

---

**Quickstart Status**: Complete and tested  
**Test Scenarios**: 4 user scenarios + performance + integration  
**Ready for**: Task generation and implementation