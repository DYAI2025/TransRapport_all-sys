<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  
  let isRecording = false;
  let audioLevel = 0;
  let currentSpeaker = null;
  let realtimeMarkers = [];
  let elapsedTime = 0;
  let sessionActive = false;
  
  // Real-time analysis status
  let analysisStatus = {
    constitutional_compliance: 'ACTIVE',
    engines_active: ['ATO', 'SEM', 'CLU', 'MEMA'],
    current_segment: null,
    total_segments: 0,
    markers_detected: 0
  };
  
  // Demo real-time data
  let demoTranscript = [
    { speaker: 'Speaker 1', text: 'Let me start by outlining our quarterly objectives...', timestamp: '00:00:02', markers: ['CLU'] },
    { speaker: 'Speaker 2', text: 'That sounds like a comprehensive approach to our planning.', timestamp: '00:00:08', markers: ['CLU'] },
    { speaker: 'Speaker 1', text: 'Actually, I want to revisit the budget allocation strategy.', timestamp: '00:00:15', markers: ['ATO'] },
    { speaker: 'Speaker 2', text: 'Yes, that makes sense given the current market dynamics.', timestamp: '00:00:22', markers: ['CLU'] }
  ];
  
  let currentTranscriptIndex = 0;
  let sessionInterval = null;
  let audioAnimation = null;
  
  onMount(() => {
    // Simulate audio level fluctuations
    audioAnimation = setInterval(() => {
      if (isRecording) {
        audioLevel = Math.random() * 100;
      } else {
        audioLevel = 0;
      }
    }, 100);
  });
  
  onDestroy(() => {
    stopSession();
    if (audioAnimation) clearInterval(audioAnimation);
  });
  
  function startSession() {
    sessionActive = true;
    isRecording = true;
    elapsedTime = 0;
    currentTranscriptIndex = 0;
    realtimeMarkers = [];
    analysisStatus.total_segments = 0;
    analysisStatus.markers_detected = 0;
    
    // Start session timer
    sessionInterval = setInterval(() => {
      elapsedTime++;
      
      // Simulate transcript updates
      if (elapsedTime % 8 === 0 && currentTranscriptIndex < demoTranscript.length) {
        const segment = demoTranscript[currentTranscriptIndex];
        analysisStatus.current_segment = segment;
        analysisStatus.total_segments++;
        
        // Add markers
        segment.markers.forEach(markerType => {
          realtimeMarkers.push({
            id: `marker_${Date.now()}_${Math.random()}`,
            type: markerType,
            confidence: 0.7 + Math.random() * 0.3,
            segment: currentTranscriptIndex + 1,
            timestamp: formatTime(elapsedTime),
            description: getMarkerDescription(markerType)
          });
          analysisStatus.markers_detected++;
        });
        
        currentTranscriptIndex++;
        
        // Trigger reactive updates
        realtimeMarkers = [...realtimeMarkers];
      }
    }, 1000);
  }
  
  function stopSession() {
    sessionActive = false;
    isRecording = false;
    if (sessionInterval) {
      clearInterval(sessionInterval);
      sessionInterval = null;
    }
    currentSpeaker = null;
    analysisStatus.current_segment = null;
  }
  
  function pauseSession() {
    isRecording = !isRecording;
  }
  
  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  
  function getMarkerDescription(type) {
    const descriptions = {
      'ATO': 'Attention shift detected',
      'SEM': 'Semantic marker identified',
      'CLU': 'Clustering behavior observed',
      'MEMA': 'Memory pattern detected'
    };
    return descriptions[type] || 'Constitutional marker detected';
  }
  
  function getMarkerColor(type) {
    const colors = {
      'ATO': '#667eea',
      'SEM': '#764ba2',
      'CLU': '#f093fb', 
      'MEMA': '#4facfe'
    };
    return colors[type] || '#64748b';
  }
  
  function exportSession() {
    console.log('Exporting real-time session...');
    // Would integrate with export library
  }
</script>

<div class="realtime-monitor">
  <div class="monitor-header">
    <div class="header-info">
      <h2 class="monitor-title">
        <span class="title-icon">🎙️</span>
        Live Constitutional Analysis
      </h2>
      <p class="monitor-subtitle">Real-time LD-3.4 marker detection and rapport analysis</p>
    </div>
    
    <div class="session-controls">
      {#if !sessionActive}
        <button class="control-btn start" on:click={startSession}>
          <span class="btn-icon">▶️</span>
          Start Session
        </button>
      {:else}
        <button class="control-btn pause" on:click={pauseSession}>
          <span class="btn-icon">{isRecording ? '⏸️' : '▶️'}</span>
          {isRecording ? 'Pause' : 'Resume'}
        </button>
        <button class="control-btn stop" on:click={stopSession}>
          <span class="btn-icon">⏹️</span>
          Stop
        </button>
        <button class="control-btn export" on:click={exportSession}>
          <span class="btn-icon">📤</span>
          Export
        </button>
      {/if}
    </div>
  </div>
  
  <div class="monitor-grid">
    <!-- Audio Status Panel -->
    <div class="panel audio-panel">
      <div class="panel-header">
        <h3>🎵 Audio Status</h3>
        <span class="status-indicator" class:active={isRecording}>
          {isRecording ? 'RECORDING' : 'STANDBY'}
        </span>
      </div>
      
      <div class="audio-visualizer">
        <div class="audio-level-container">
          <div class="audio-level" style="height: {audioLevel}%"></div>
        </div>
        <div class="audio-info">
          <div class="info-item">
            <span class="info-label">Level:</span>
            <span class="info-value">{audioLevel.toFixed(0)}%</span>
          </div>
          <div class="info-item">
            <span class="info-label">Duration:</span>
            <span class="info-value">{formatTime(elapsedTime)}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Current Speaker:</span>
            <span class="info-value">{analysisStatus.current_segment?.speaker || 'None'}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Constitutional Analysis Status -->
    <div class="panel analysis-panel">
      <div class="panel-header">
        <h3>🏛️ Constitutional Status</h3>
        <span class="compliance-badge verified">{analysisStatus.constitutional_compliance}</span>
      </div>
      
      <div class="analysis-grid">
        <div class="stat-box">
          <span class="stat-icon">📊</span>
          <div class="stat-content">
            <span class="stat-value">{analysisStatus.total_segments}</span>
            <span class="stat-label">Segments</span>
          </div>
        </div>
        <div class="stat-box">
          <span class="stat-icon">🎯</span>
          <div class="stat-content">
            <span class="stat-value">{analysisStatus.markers_detected}</span>
            <span class="stat-label">Markers</span>
          </div>
        </div>
        <div class="stat-box">
          <span class="stat-icon">⚡</span>
          <div class="stat-content">
            <span class="stat-value">{analysisStatus.engines_active.length}</span>
            <span class="stat-label">Engines</span>
          </div>
        </div>
        <div class="stat-box">
          <span class="stat-icon">🔒</span>
          <div class="stat-content">
            <span class="stat-value">LD-3.4</span>
            <span class="stat-label">Framework</span>
          </div>
        </div>
      </div>
      
      <div class="engines-status">
        <h4>Analysis Engines</h4>
        <div class="engines-grid">
          {#each analysisStatus.engines_active as engine}
            <div class="engine-status">
              <span class="engine-name">{engine}</span>
              <span class="engine-indicator active"></span>
            </div>
          {/each}
        </div>
      </div>
    </div>
    
    <!-- Live Transcript -->
    <div class="panel transcript-panel">
      <div class="panel-header">
        <h3>📝 Live Transcript</h3>
        <span class="transcript-status">{analysisStatus.current_segment ? 'ACTIVE' : 'WAITING'}</span>
      </div>
      
      <div class="transcript-content">
        {#if analysisStatus.current_segment}
          <div class="current-segment">
            <div class="segment-header">
              <span class="speaker">{analysisStatus.current_segment.speaker}</span>
              <span class="timestamp">{analysisStatus.current_segment.timestamp}</span>
            </div>
            <div class="segment-text">{analysisStatus.current_segment.text}</div>
            {#if analysisStatus.current_segment.markers.length > 0}
              <div class="segment-markers">
                {#each analysisStatus.current_segment.markers as marker}
                  <span class="marker-tag" style="background-color: {getMarkerColor(marker)}">
                    {marker}
                  </span>
                {/each}
              </div>
            {/if}
          </div>
        {:else}
          <div class="transcript-placeholder">
            <span class="placeholder-icon">🎤</span>
            <p>Waiting for audio input...</p>
            <p class="placeholder-hint">Start a session to begin real-time transcription and analysis</p>
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Real-time Markers -->
    <div class="panel markers-panel">
      <div class="panel-header">
        <h3>🎯 Live Markers</h3>
        <span class="markers-count">{realtimeMarkers.length} detected</span>
      </div>
      
      <div class="markers-feed">
        {#if realtimeMarkers.length > 0}
          {#each realtimeMarkers.slice(-5) as marker (marker.id)}
            <div class="marker-item">
              <div class="marker-info">
                <span class="marker-type" style="background-color: {getMarkerColor(marker.type)}">
                  {marker.type}
                </span>
                <span class="marker-confidence">{(marker.confidence * 100).toFixed(0)}%</span>
              </div>
              <div class="marker-details">
                <div class="marker-description">{marker.description}</div>
                <div class="marker-meta">
                  <span>Segment {marker.segment}</span>
                  <span>•</span>
                  <span>{marker.timestamp}</span>
                </div>
              </div>
            </div>
          {/each}
        {:else}
          <div class="markers-placeholder">
            <span class="placeholder-icon">🏛️</span>
            <p>No markers detected yet</p>
            <p class="placeholder-hint">Constitutional markers will appear here during analysis</p>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .realtime-monitor {
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .monitor-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 2rem;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  }

  .header-info {
    flex: 1;
  }

  .monitor-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.8rem;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 0.5rem;
  }

  .title-icon {
    font-size: 2rem;
  }

  .monitor-subtitle {
    color: #64748b;
    font-size: 1.1rem;
    margin: 0;
  }

  .session-controls {
    display: flex;
    gap: 1rem;
  }

  .control-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .control-btn.start {
    background: linear-gradient(135deg, #38a169, #48bb78);
    color: white;
  }

  .control-btn.pause {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
  }

  .control-btn.stop {
    background: linear-gradient(135deg, #e53e3e, #fc8181);
    color: white;
  }

  .control-btn.export {
    background: linear-gradient(135deg, #805ad5, #9f7aea);
    color: white;
  }

  .control-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
  }

  .btn-icon {
    font-size: 1.1rem;
  }

  .monitor-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
    gap: 1.5rem;
    flex: 1;
    min-height: 0;
  }

  .panel {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e2e8f0;
  }

  .panel-header h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #2d3748;
  }

  .status-indicator {
    padding: 0.4rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 600;
    background: #fed7d7;
    color: #c53030;
  }

  .status-indicator.active {
    background: #c6f6d5;
    color: #22543d;
    animation: pulse 2s infinite;
  }

  .compliance-badge {
    padding: 0.4rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .compliance-badge.verified {
    background: #c6f6d5;
    color: #22543d;
  }

  .audio-visualizer {
    display: flex;
    gap: 2rem;
    align-items: center;
    flex: 1;
  }

  .audio-level-container {
    width: 60px;
    height: 150px;
    background: #f1f5f9;
    border-radius: 30px;
    position: relative;
    overflow: hidden;
  }

  .audio-level {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, #38a169, #68d391, #9ae6b4);
    border-radius: 30px;
    transition: height 0.1s ease;
  }

  .audio-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: #f8fafc;
    border-radius: 8px;
  }

  .info-label {
    color: #64748b;
    font-weight: 500;
  }

  .info-value {
    font-weight: 600;
    color: #2d3748;
  }

  .analysis-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .stat-box {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
  }

  .stat-icon {
    font-size: 1.5rem;
  }

  .stat-content {
    display: flex;
    flex-direction: column;
  }

  .stat-value {
    font-size: 1.2rem;
    font-weight: 700;
    color: #2d3748;
  }

  .stat-label {
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .engines-status h4 {
    margin: 0 0 1rem 0;
    color: #4a5568;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .engines-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }

  .engine-status {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: #f8fafc;
    border-radius: 6px;
  }

  .engine-name {
    font-weight: 600;
    color: #2d3748;
    font-size: 0.9rem;
  }

  .engine-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #fed7d7;
  }

  .engine-indicator.active {
    background: #68d391;
    box-shadow: 0 0 10px rgba(104, 211, 145, 0.6);
    animation: pulse 2s infinite;
  }

  .transcript-content {
    flex: 1;
    min-height: 120px;
  }

  .current-segment {
    padding: 1.5rem;
    background: linear-gradient(135deg, #f8faff 0%, #f1f5ff 100%);
    border-radius: 8px;
    border-left: 4px solid #667eea;
  }

  .segment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .speaker {
    font-weight: 600;
    color: #667eea;
  }

  .timestamp {
    font-size: 0.8rem;
    color: #64748b;
    font-family: monospace;
  }

  .segment-text {
    color: #2d3748;
    line-height: 1.6;
    margin-bottom: 1rem;
  }

  .segment-markers {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .marker-tag {
    padding: 0.3rem 0.7rem;
    color: white;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .transcript-placeholder, .markers-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    text-align: center;
    color: #64748b;
    height: 100%;
  }

  .placeholder-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .placeholder-hint {
    font-size: 0.9rem;
    opacity: 0.7;
  }

  .transcript-status, .markers-count {
    padding: 0.3rem 0.6rem;
    background: #e2e8f0;
    color: #4a5568;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .markers-feed {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-height: 120px;
  }

  .marker-item {
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
    border-left: 4px solid #667eea;
  }

  .marker-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .marker-type {
    padding: 0.3rem 0.8rem;
    color: white;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .marker-confidence {
    padding: 0.2rem 0.5rem;
    background: #e2e8f0;
    color: #4a5568;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .marker-description {
    color: #2d3748;
    font-weight: 500;
    margin-bottom: 0.5rem;
  }

  .marker-meta {
    display: flex;
    gap: 0.5rem;
    color: #64748b;
    font-size: 0.8rem;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.6;
    }
  }
</style>