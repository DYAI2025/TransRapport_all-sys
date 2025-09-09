<script>
  import { onMount } from 'svelte';
  import * as cli from '../lib/cli-service';
  
  // UI State  
  let currentSession = '';
  let sessionStatus = 'idle'; // 'idle' | 'recording' | 'transcribing' | 'diarizing' | 'analyzing' | 'completed'
  let isRecording = false;
  let processingStep = '';
  let progress = 0;
  let logs = [];
  let audioDevices = [];
  let selectedDevice = '';
  
  // Analysis Results
  let transcriptionResult = null;
  let diarizationResult = null;
  let analysisEvents = {
    ato: [],
    sem: [],
    clu: [],
    mema: []
  };
  let activeEventView = 'ato';
  
  // LLM Assist Toggle (disabled)
  let llmAssistEnabled = false;
  
  // Session Management
  let sessions = [];
  
  onMount(async () => {
    await loadAudioDevices();
    await loadSessions();
    addLog('TransRapport Desktop UI initialized');
    addLog('Constitutional Framework: LD-3.4');
    addLog('Mode: Offline only');
  });
  
  function addLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    logs = [`[${timestamp}] ${message}`, ...logs].slice(0, 50); // Keep last 50 logs
  }
  
  async function loadAudioDevices() {
    try {
      const result = await cli.getAudioDevices();
      if (result.success && result.data) {
        audioDevices = result.data;
        selectedDevice = audioDevices.find(d => d.is_default)?.id || audioDevices[0]?.id || '';
        addLog(`Loaded ${audioDevices.length} audio devices`);
      }
    } catch (error) {
      addLog(`Failed to load audio devices: ${error}`);
    }
  }
  
  async function loadSessions() {
    // Mock session loading - in real app would call CLI to list sessions
    sessions = [
      {
        id: 'demo-session',
        name: 'Demo Session',
        status: 'idle',
        created: new Date().toISOString(),
        files: {}
      }
    ];
  }
  
  function generateSessionId() {
    return `session-${Date.now()}`;
  }
  
  // Button Actions
  
  async function startRecording() {
    if (!currentSession) {
      currentSession = generateSessionId();
    }
    
    try {
      processingStep = 'Starting recording...';
      const result = await cli.startRecording(currentSession, selectedDevice);
      
      if (result.success) {
        isRecording = true;
        sessionStatus = 'recording';
        addLog(`Recording started for session: ${currentSession}`);
        addLog(result.stdout || 'Recording active');
      } else {
        addLog(`Recording failed: ${result.error}`);
      }
    } catch (error) {
      addLog(`Recording error: ${error}`);
    } finally {
      processingStep = '';
    }
  }
  
  async function stopRecording() {
    if (!isRecording || !currentSession) return;
    
    try {
      processingStep = 'Stopping recording...';
      const outputPath = `./sessions/${currentSession}/raw.wav`;
      const result = await cli.stopRecording(currentSession, outputPath);
      
      if (result.success) {
        isRecording = false;
        sessionStatus = 'idle';
        addLog(`Recording stopped for session: ${currentSession}`);
        addLog(result.stdout || 'Recording saved');
        
        // Update session info
        const session = sessions.find(s => s.id === currentSession);
        if (session) {
          session.files.raw_audio = outputPath;
          sessions = [...sessions];
        }
      } else {
        addLog(`Stop recording failed: ${result.error}`);
      }
    } catch (error) {
      addLog(`Stop recording error: ${error}`);
    } finally {
      processingStep = '';
    }
  }
  
  async function importFile() {
    // Mock file import - in real app would use Tauri file dialog
    if (!currentSession) {
      currentSession = generateSessionId();
    }
    
    const mockFile = '../samples/test.txt';
    try {
      processingStep = 'Importing file...';
      const result = await cli.importTextFile(currentSession, mockFile, 'Imported file');
      
      if (result.success) {
        addLog(`File imported for session: ${currentSession}`);
        addLog(result.stdout || 'Import completed');
      } else {
        addLog(`Import failed: ${result.error}`);
      }
    } catch (error) {
      addLog(`Import error: ${error}`);
    } finally {
      processingStep = '';
    }
  }
  
  async function transcribeAudio() {
    if (!currentSession) {
      addLog('No active session for transcription');
      return;
    }
    
    try {
      sessionStatus = 'transcribing';
      processingStep = 'Transcribing audio...';
      progress = 0;
      
      // Simulate progress
      const progressInterval = setInterval(() => {
        progress = Math.min(progress + 10, 90);
      }, 200);
      
      const result = await cli.transcribe(currentSession, 'base', 'de');
      clearInterval(progressInterval);
      progress = 100;
      
      if (result.success) {
        transcriptionResult = result.data;
        sessionStatus = 'idle';
        addLog(`Transcription completed for session: ${currentSession}`);
        addLog(`Language: ${result.data?.language}, Duration: ${result.data?.duration}s`);
        
        // Update session info
        const session = sessions.find(s => s.id === currentSession);
        if (session) {
          session.files.transcript = `./sessions/${currentSession}/transcript.json`;
          session.duration = result.data?.duration;
          sessions = [...sessions];
        }
      } else {
        addLog(`Transcription failed: ${result.error}`);
        sessionStatus = 'idle';
      }
    } catch (error) {
      addLog(`Transcription error: ${error}`);
      sessionStatus = 'idle';
    } finally {
      processingStep = '';
      progress = 0;
    }
  }
  
  async function performDiarization() {
    if (!currentSession) {
      addLog('No active session for diarization');
      return;
    }
    
    try {
      sessionStatus = 'diarizing';
      processingStep = 'Performing speaker diarization...';
      progress = 0;
      
      const progressInterval = setInterval(() => {
        progress = Math.min(progress + 8, 85);
      }, 300);
      
      const result = await cli.diarize(currentSession, 1.5);
      clearInterval(progressInterval);
      progress = 100;
      
      if (result.success) {
        diarizationResult = result.data;
        sessionStatus = 'idle';
        addLog(`Diarization completed for session: ${currentSession}`);
        addLog(`Speakers detected: ${result.data?.speakers?.length}`);
        
        // Update session info
        const session = sessions.find(s => s.id === currentSession);
        if (session) {
          session.files.diarization = `./sessions/${currentSession}/diarization.json`;
          sessions = [...sessions];
        }
      } else {
        addLog(`Diarization failed: ${result.error}`);
        sessionStatus = 'idle';
      }
    } catch (error) {
      addLog(`Diarization error: ${error}`);
      sessionStatus = 'idle';
    } finally {
      processingStep = '';
      progress = 0;
    }
  }
  
  async function runAnalysis() {
    if (!currentSession) {
      addLog('No active session for analysis');
      return;
    }
    
    try {
      sessionStatus = 'analyzing';
      processingStep = 'Running LD-3.4 constitutional analysis...';
      progress = 0;
      
      const progressInterval = setInterval(() => {
        progress = Math.min(progress + 5, 80);
      }, 400);
      
      const result = await cli.analyze(currentSession);
      clearInterval(progressInterval);
      progress = 100;
      
      if (result.success) {
        sessionStatus = 'completed';
        addLog(`LD-3.4 analysis completed for session: ${currentSession}`);
        addLog('Constitutional markers detected and analyzed');
        
        // Load analysis results
        await loadAnalysisEvents();
        
        // Update session info
        const session = sessions.find(s => s.id === currentSession);
        if (session) {
          session.status = 'completed';
          session.files.analysis = `./sessions/${currentSession}/analysis.json`;
          sessions = [...sessions];
        }
      } else {
        addLog(`Analysis failed: ${result.error}`);
        sessionStatus = 'idle';
      }
    } catch (error) {
      addLog(`Analysis error: ${error}`);
      sessionStatus = 'idle';
    } finally {
      processingStep = '';
      progress = 0;
    }
  }
  
  async function loadAnalysisEvents() {
    if (!currentSession) return;
    
    try {
      for (const level of ['ato', 'sem', 'clu', 'mema']) {
        let result;
        switch (level) {
          case 'ato':
            result = await cli.viewATO(currentSession, 200);
            break;
          case 'sem':
            result = await cli.viewSEM(currentSession, 200);
            break;
          case 'clu':
            result = await cli.viewCLU(currentSession, 200);
            break;
          case 'mema':
            result = await cli.viewMEMA(currentSession, 200);
            break;
          default:
            throw new Error(`Unknown event level: ${level}`);
        }
        if (result.success && result.data) {
          const events = Array.isArray(result.data) ? result.data : result.data.events || [];
          analysisEvents[level] = events;
        }
      }
    } catch (error) {
      addLog(`Failed to load analysis events: ${error}`);
    }
  }
  
  async function exportReport() {
    if (!currentSession) {
      addLog('No active session for export');
      return;
    }
    
    try {
      processingStep = 'Exporting report...';
      const result = await cli.exportReport(currentSession, 'pdf');
      
      if (result.success) {
        addLog(`Report exported for session: ${currentSession}`);
        addLog(result.stdout || 'Export completed');
      } else {
        addLog(`Export failed: ${result.error}`);
      }
    } catch (error) {
      addLog(`Export error: ${error}`);
    } finally {
      processingStep = '';
    }
  }
  
  async function exportData() {
    if (!currentSession) {
      addLog('No active session for data export');
      return;
    }
    
    try {
      processingStep = 'Exporting data...';
      const result = await cli.exportData(currentSession);
      
      if (result.success) {
        addLog(`Data exported for session: ${currentSession}`);
        addLog(result.stdout || 'Data export completed');
      } else {
        addLog(`Data export failed: ${result.error}`);
      }
    } catch (error) {
      addLog(`Data export error: ${error}`);
    } finally {
      processingStep = '';
    }
  }
</script>

<div class="workflow-container">
  <!-- Header -->
  <div class="header">
    <div class="header-left">
      <h1>🏛️ TransRapport Desktop</h1>
      <div class="session-info">
        <span class="label">Session:</span>
        <input bind:value={currentSession} placeholder="Enter session ID or generate new" />
        <span class="status status-{sessionStatus}">{sessionStatus}</span>
      </div>
    </div>
    <div class="header-right">
      <div class="llm-toggle">
        <label>
          <input type="checkbox" bind:checked={llmAssistEnabled} disabled />
          LLM Assist (Disabled)
        </label>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div class="main-content">
    <!-- Control Panel -->
    <div class="control-panel">
      <div class="section">
        <h3>🎤 Audio Recording</h3>
        <div class="controls">
          <select bind:value={selectedDevice}>
            {#each audioDevices as device}
              <option value={device.id}>{device.name} {device.is_default ? '(Default)' : ''}</option>
            {/each}
          </select>
          <button 
            on:click={startRecording} 
            disabled={isRecording || sessionStatus !== 'idle'}
            class="btn btn-record"
          >
            🔴 Start Recording
          </button>
          <button 
            on:click={stopRecording} 
            disabled={!isRecording}
            class="btn btn-stop"
          >
            ⏹️ Stop Recording
          </button>
        </div>
      </div>

      <div class="section">
        <h3>📁 File Import</h3>
        <div class="controls">
          <button 
            on:click={importFile}
            disabled={sessionStatus !== 'idle'}
            class="btn btn-import"
          >
            📂 Import File
          </button>
        </div>
      </div>

      <div class="section">
        <h3>🔄 Processing Pipeline</h3>
        <div class="controls pipeline">
          <button 
            on:click={transcribeAudio}
            disabled={sessionStatus !== 'idle' || !currentSession}
            class="btn btn-process"
          >
            🎙️ Transcribe
          </button>
          <button 
            on:click={performDiarization}
            disabled={sessionStatus !== 'idle' || !currentSession}
            class="btn btn-process"
          >
            👥 Diarize
          </button>
          <button 
            on:click={runAnalysis}
            disabled={sessionStatus !== 'idle' || !currentSession}
            class="btn btn-process"
          >
            🏛️ Analyze
          </button>
        </div>
      </div>

      <div class="section">
        <h3>📊 View Results</h3>
        <div class="controls">
          <div class="event-buttons">
            {#each ['ato', 'sem', 'clu', 'mema'] as eventType}
              <button 
                on:click={() => { activeEventView = eventType; loadAnalysisEvents(); }}
                class="btn btn-view {activeEventView === eventType ? 'active' : ''}"
                disabled={sessionStatus !== 'completed'}
              >
                {eventType.toUpperCase()} ({analysisEvents[eventType]?.length || 0})
              </button>
            {/each}
          </div>
        </div>
      </div>

      <div class="section">
        <h3>📤 Export</h3>
        <div class="controls">
          <button 
            on:click={exportReport}
            disabled={sessionStatus !== 'completed'}
            class="btn btn-export"
          >
            📋 Export Report
          </button>
          <button 
            on:click={exportData}
            disabled={sessionStatus !== 'completed'}
            class="btn btn-export"
          >
            💾 Export Data
          </button>
        </div>
      </div>
    </div>

    <!-- Results Panel -->
    <div class="results-panel">
      <!-- Progress Bar -->
      {#if processingStep}
        <div class="progress-section">
          <div class="progress-label">{processingStep}</div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%"></div>
          </div>
        </div>
      {/if}

      <!-- Results Display -->
      <div class="results-content">
        {#if transcriptionResult}
          <div class="result-section">
            <h4>📝 Transcription</h4>
            <div class="result-data">
              <p><strong>Language:</strong> {transcriptionResult.language}</p>
              <p><strong>Duration:</strong> {transcriptionResult.duration}s</p>
              <div class="transcript">{transcriptionResult.text}</div>
            </div>
          </div>
        {/if}

        {#if diarizationResult}
          <div class="result-section">
            <h4>👥 Speaker Diarization</h4>
            <div class="result-data">
              <div class="speakers">
                {#each diarizationResult.speakers as speaker}
                  <div class="speaker">
                    <span class="speaker-id">{speaker.id}</span>
                    <span class="speaker-time">{speaker.speaking_time.toFixed(1)}s</span>
                    <span class="speaker-segments">{speaker.segment_count} segments</span>
                  </div>
                {/each}
              </div>
            </div>
          </div>
        {/if}

        {#if sessionStatus === 'completed' && analysisEvents[activeEventView]?.length}
          <div class="result-section">
            <h4>🏛️ Constitutional Markers - {activeEventView.toUpperCase()}</h4>
            <div class="result-data">
              <div class="events-list">
                {#each analysisEvents[activeEventView].slice(0, 10) as event}
                  <div class="event-item">
                    <span class="event-time">{event.start_time.toFixed(1)}s</span>
                    <span class="event-type">{event.marker_subtype}</span>
                    <span class="event-confidence">{(event.confidence * 100).toFixed(0)}%</span>
                    <span class="event-evidence">{event.evidence.substring(0, 50)}...</span>
                  </div>
                {/each}
              </div>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Logs Panel -->
  <div class="logs-panel">
    <h4>📋 System Logs</h4>
    <div class="logs-content">
      {#each logs as log}
        <div class="log-entry">{log}</div>
      {/each}
    </div>
  </div>
</div>

<style>
  .workflow-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #f8fafc;
    font-family: 'Segoe UI', system-ui, sans-serif;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }

  .header h1 {
    margin: 0;
    font-size: 1.5rem;
  }

  .session-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  .session-info input {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    border: none;
    max-width: 200px;
  }

  .status {
    padding: 0.25rem 0.5rem;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .status-idle { background: rgba(255,255,255,0.2); }
  .status-recording { background: #dc2626; }
  .status-transcribing { background: #059669; }
  .status-diarizing { background: #7c3aed; }
  .status-analyzing { background: #dc2626; }
  .status-completed { background: #059669; }

  .llm-toggle label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    opacity: 0.6;
    font-size: 0.9rem;
  }

  .main-content {
    display: flex;
    flex: 1;
    gap: 2rem;
    padding: 2rem;
    overflow: hidden;
  }

  .control-panel {
    width: 400px;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .section {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  }

  .section h3 {
    margin: 0 0 1rem 0;
    color: #2d3748;
    font-size: 1.1rem;
  }

  .controls {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .controls.pipeline {
    flex-direction: row;
    gap: 0.5rem;
  }

  .btn {
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.9rem;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-record { background: #dc2626; color: white; }
  .btn-stop { background: #374151; color: white; }
  .btn-import { background: #059669; color: white; }
  .btn-process { background: #7c3aed; color: white; flex: 1; }
  .btn-view { background: #e5e7eb; color: #374151; }
  .btn-view.active { background: #667eea; color: white; }
  .btn-export { background: #f59e0b; color: white; }

  .btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  }

  .event-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }

  .results-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    overflow-y: auto;
  }

  .progress-section {
    background: white;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  }

  .progress-label {
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 0.5rem;
  }

  .progress-bar {
    width: 100%;
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    transition: width 0.3s ease;
  }

  .results-content {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .result-section {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  }

  .result-section h4 {
    margin: 0 0 1rem 0;
    color: #2d3748;
  }

  .transcript {
    background: #f8fafc;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin-top: 0.5rem;
    line-height: 1.6;
  }

  .speakers {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .speaker {
    background: #f3f4f6;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
  }

  .speaker-id {
    font-weight: 600;
    color: #667eea;
  }

  .events-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .event-item {
    display: grid;
    grid-template-columns: 60px 150px 60px 1fr;
    gap: 1rem;
    padding: 0.75rem;
    background: #f8fafc;
    border-radius: 8px;
    font-size: 0.9rem;
  }

  .event-time {
    font-weight: 600;
    color: #667eea;
  }

  .event-type {
    font-weight: 500;
  }

  .event-confidence {
    color: #059669;
    font-weight: 600;
  }

  .event-evidence {
    color: #64748b;
  }

  .logs-panel {
    height: 200px;
    background: #1f2937;
    color: #e5e7eb;
    padding: 1rem 2rem;
    overflow-y: auto;
  }

  .logs-panel h4 {
    margin: 0 0 1rem 0;
    color: white;
  }

  .logs-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .log-entry {
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 0.8rem;
    line-height: 1.4;
    opacity: 0.9;
  }

  select {
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background: white;
  }
</style>