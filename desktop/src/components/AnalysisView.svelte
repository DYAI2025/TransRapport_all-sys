<script lang="ts">
  import { onMount } from 'svelte';
  
  export let conversation;
  
  let analysisData = null;
  let selectedSegment = null;
  let markersExpanded = true;
  let transcriptExpanded = true;
  
  // Simulated detailed analysis data
  onMount(() => {
    if (conversation) {
      analysisData = {
        segments: [
          {
            id: 'seg_001',
            speaker: 'Speaker 1',
            text: 'I think we should focus on the quarterly results and how they align with our strategic objectives.',
            start_time: 0.0,
            end_time: 4.2,
            markers: [
              {
                type: 'CLU',
                confidence: 0.85,
                position: 'we should focus',
                description: 'Collective attention clustering detected'
              }
            ]
          },
          {
            id: 'seg_002',
            speaker: 'Speaker 2',
            text: 'Yes, exactly! That makes perfect sense given the current market conditions.',
            start_time: 4.5,
            end_time: 8.1,
            markers: [
              {
                type: 'CLU',
                confidence: 0.92,
                position: 'Yes, exactly!',
                description: 'Strong agreement clustering marker'
              }
            ]
          },
          {
            id: 'seg_003',
            speaker: 'Speaker 1',
            text: 'So we both agree that the revenue targets are achievable within this timeframe.',
            start_time: 8.4,
            end_time: 12.8,
            markers: [
              {
                type: 'CLU',
                confidence: 0.78,
                position: 'we both agree',
                description: 'Consensus formation detected'
              }
            ]
          },
          {
            id: 'seg_004',
            speaker: 'Speaker 2',
            text: 'Actually, I have some concerns about the implementation timeline. Let me clarify my position.',
            start_time: 13.2,
            end_time: 17.5,
            markers: [
              {
                type: 'ATO',
                confidence: 0.73,
                position: 'Actually, I have some concerns',
                description: 'Attention shift marker detected'
              }
            ]
          }
        ],
        constitutional_analysis: {
          compliance_status: 'VERIFIED',
          framework_version: 'LD-3.4',
          analysis_method: 'Constitutional Marker Detection',
          total_markers: 4,
          marker_breakdown: {
            'ATO': 1,
            'SEM': 0,
            'CLU': 3,
            'MEMA': 0
          },
          rapport_score: 0.72,
          confidence_avg: 0.82
        }
      };
    }
  });
  
  function selectSegment(segment) {
    selectedSegment = segment;
  }
  
  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(1);
    return `${mins}:${secs.padStart(4, '0')}`;
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
  
  function getMarkerLabel(type) {
    const labels = {
      'ATO': 'Attention',
      'SEM': 'Semantic',
      'CLU': 'Cluster',
      'MEMA': 'Memory'
    };
    return labels[type] || type;
  }
</script>

<div class="analysis-view">
  <div class="analysis-header">
    <div class="conversation-info">
      <h2 class="conversation-title">{conversation.name}</h2>
      <p class="conversation-meta">{conversation.description}</p>
      <div class="analysis-badges">
        <span class="badge constitutional">🏛️ LD-3.4 Compliant</span>
        <span class="badge status">{conversation.stats.constitutional_compliance}</span>
      </div>
    </div>
    
    <div class="analysis-stats">
      <div class="stat-card">
        <span class="stat-icon">📊</span>
        <div class="stat-content">
          <span class="stat-value">{analysisData?.constitutional_analysis?.total_markers || 0}</span>
          <span class="stat-label">Total Markers</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">🤝</span>
        <div class="stat-content">
          <span class="stat-value">{analysisData?.constitutional_analysis?.rapport_score?.toFixed(2) || '0.00'}</span>
          <span class="stat-label">Rapport Score</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">⚡</span>
        <div class="stat-content">
          <span class="stat-value">{analysisData?.constitutional_analysis?.confidence_avg?.toFixed(1) || '0.0'}%</span>
          <span class="stat-label">Avg Confidence</span>
        </div>
      </div>
    </div>
  </div>
  
  <div class="analysis-content">
    <div class="left-panel">
      <!-- Constitutional Markers Summary -->
      <div class="panel-section">
        <div class="section-header" on:click={() => markersExpanded = !markersExpanded}>
          <h3>🏛️ Constitutional Markers</h3>
          <span class="expand-icon" class:expanded={markersExpanded}>▼</span>
        </div>
        
        {#if markersExpanded && analysisData}
          <div class="markers-grid">
            {#each Object.entries(analysisData.constitutional_analysis.marker_breakdown) as [type, count]}
              <div class="marker-summary" style="border-left-color: {getMarkerColor(type)}">
                <div class="marker-info">
                  <span class="marker-type">{getMarkerLabel(type)}</span>
                  <span class="marker-count">{count} detected</span>
                </div>
                <div class="marker-badge" style="background-color: {getMarkerColor(type)}">
                  {type}
                </div>
              </div>
            {/each}
          </div>
          
          <div class="constitutional-compliance">
            <div class="compliance-header">
              <span class="compliance-icon">🏛️</span>
              <span class="compliance-text">Constitutional Analysis</span>
            </div>
            <div class="compliance-details">
              <div class="detail-item">
                <span class="detail-label">Framework:</span>
                <span class="detail-value">{analysisData.constitutional_analysis.framework_version}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Method:</span>
                <span class="detail-value">{analysisData.constitutional_analysis.analysis_method}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Status:</span>
                <span class="detail-value verified">{analysisData.constitutional_analysis.compliance_status}</span>
              </div>
            </div>
          </div>
        {/if}
      </div>
      
      <!-- Segment Analysis -->
      <div class="panel-section">
        <div class="section-header" on:click={() => transcriptExpanded = !transcriptExpanded}>
          <h3>📝 Transcript Analysis</h3>
          <span class="expand-icon" class:expanded={transcriptExpanded}>▼</span>
        </div>
        
        {#if transcriptExpanded && analysisData}
          <div class="segments-list">
            {#each analysisData.segments as segment}
              <div 
                class="segment-item" 
                class:selected={selectedSegment?.id === segment.id}
                on:click={() => selectSegment(segment)}
              >
                <div class="segment-header">
                  <span class="speaker-label">{segment.speaker}</span>
                  <span class="time-range">{formatTime(segment.start_time)} - {formatTime(segment.end_time)}</span>
                </div>
                <div class="segment-text">{segment.text}</div>
                
                {#if segment.markers.length > 0}
                  <div class="segment-markers">
                    {#each segment.markers as marker}
                      <div class="marker-chip" style="background-color: {getMarkerColor(marker.type)}">
                        <span class="marker-type-small">{marker.type}</span>
                        <span class="marker-confidence">{(marker.confidence * 100).toFixed(0)}%</span>
                      </div>
                    {/each}
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
    
    <div class="right-panel">
      {#if selectedSegment}
        <div class="detail-panel">
          <h3>🔍 Segment Details</h3>
          
          <div class="segment-details">
            <div class="detail-group">
              <h4>Speaker Information</h4>
              <div class="detail-row">
                <span class="label">Speaker:</span>
                <span class="value">{selectedSegment.speaker}</span>
              </div>
              <div class="detail-row">
                <span class="label">Duration:</span>
                <span class="value">{(selectedSegment.end_time - selectedSegment.start_time).toFixed(1)}s</span>
              </div>
              <div class="detail-row">
                <span class="label">Time Range:</span>
                <span class="value">{formatTime(selectedSegment.start_time)} - {formatTime(selectedSegment.end_time)}</span>
              </div>
            </div>
            
            <div class="detail-group">
              <h4>Transcript</h4>
              <div class="transcript-text">{selectedSegment.text}</div>
            </div>
            
            {#if selectedSegment.markers.length > 0}
              <div class="detail-group">
                <h4>Constitutional Markers</h4>
                {#each selectedSegment.markers as marker}
                  <div class="marker-detail">
                    <div class="marker-header">
                      <span class="marker-type-badge" style="background-color: {getMarkerColor(marker.type)}">
                        {marker.type}
                      </span>
                      <span class="marker-confidence-badge">{(marker.confidence * 100).toFixed(1)}% confidence</span>
                    </div>
                    <div class="marker-position">
                      <strong>Position:</strong> "{marker.position}"
                    </div>
                    <div class="marker-description">
                      <strong>Analysis:</strong> {marker.description}
                    </div>
                  </div>
                {/each}
              </div>
            {:else}
              <div class="detail-group">
                <h4>Constitutional Markers</h4>
                <p class="no-markers">No constitutional markers detected in this segment.</p>
              </div>
            {/if}
          </div>
        </div>
      {:else}
        <div class="empty-detail">
          <span class="empty-icon">👆</span>
          <h3>Select a Segment</h3>
          <p>Click on any transcript segment to view detailed constitutional marker analysis.</p>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .analysis-view {
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .analysis-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 2rem;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  }

  .conversation-info {
    flex: 1;
  }

  .conversation-title {
    font-size: 1.8rem;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 0.5rem;
  }

  .conversation-meta {
    color: #64748b;
    margin-bottom: 1rem;
    font-size: 1.1rem;
  }

  .analysis-badges {
    display: flex;
    gap: 0.75rem;
  }

  .badge {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
  }

  .badge.constitutional {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
  }

  .badge.status {
    background: #c6f6d5;
    color: #22543d;
  }

  .analysis-stats {
    display: flex;
    gap: 1rem;
  }

  .stat-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
    background: #f8fafc;
    border-radius: 10px;
    min-width: 140px;
  }

  .stat-icon {
    font-size: 2rem;
  }

  .stat-content {
    display: flex;
    flex-direction: column;
  }

  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #2d3748;
  }

  .stat-label {
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .analysis-content {
    display: flex;
    gap: 1.5rem;
    flex: 1;
    min-height: 0;
  }

  .left-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .right-panel {
    width: 400px;
  }

  .panel-section {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    overflow: hidden;
  }

  .section-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e2e8f0;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f8fafc;
  }

  .section-header h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #2d3748;
  }

  .expand-icon {
    transition: transform 0.2s ease;
    color: #64748b;
  }

  .expand-icon.expanded {
    transform: rotate(180deg);
  }

  .markers-grid {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .marker-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
    border-left: 4px solid;
  }

  .marker-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .marker-type {
    font-weight: 600;
    color: #2d3748;
  }

  .marker-count {
    font-size: 0.9rem;
    color: #64748b;
  }

  .marker-badge {
    padding: 0.3rem 0.8rem;
    color: white;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .constitutional-compliance {
    margin-top: 1.5rem;
    padding: 1.5rem;
    background: linear-gradient(135deg, #f8faff 0%, #f1f5ff 100%);
    border-radius: 8px;
  }

  .compliance-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    font-weight: 600;
    color: #2d3748;
  }

  .compliance-icon {
    font-size: 1.2rem;
  }

  .compliance-details {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .detail-item {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
  }

  .detail-label {
    color: #64748b;
  }

  .detail-value {
    font-weight: 600;
    color: #2d3748;
  }

  .detail-value.verified {
    color: #38a169;
  }

  .segments-list {
    padding: 1rem;
    max-height: 500px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .segment-item {
    padding: 1rem;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .segment-item:hover {
    border-color: #667eea;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
  }

  .segment-item.selected {
    border-color: #667eea;
    background: linear-gradient(135deg, #f8faff 0%, #f1f5ff 100%);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  .segment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .speaker-label {
    font-weight: 600;
    color: #667eea;
  }

  .time-range {
    font-size: 0.8rem;
    color: #64748b;
    font-family: monospace;
  }

  .segment-text {
    color: #2d3748;
    line-height: 1.5;
    margin-bottom: 0.75rem;
  }

  .segment-markers {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .marker-chip {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    color: white;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
  }

  .marker-type-small {
    font-size: 0.7rem;
  }

  .marker-confidence {
    font-size: 0.6rem;
    opacity: 0.9;
  }

  .detail-panel {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    padding: 1.5rem;
    height: 100%;
    overflow-y: auto;
  }

  .detail-panel h3 {
    margin-top: 0;
    margin-bottom: 1.5rem;
    color: #2d3748;
    font-size: 1.2rem;
  }

  .segment-details {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .detail-group h4 {
    margin: 0 0 0.75rem 0;
    color: #4a5568;
    font-size: 1rem;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.5rem;
  }

  .detail-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
  }

  .detail-row .label {
    color: #64748b;
  }

  .detail-row .value {
    font-weight: 600;
    color: #2d3748;
  }

  .transcript-text {
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
    line-height: 1.6;
    color: #2d3748;
    border-left: 4px solid #667eea;
  }

  .marker-detail {
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .marker-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .marker-type-badge {
    padding: 0.3rem 0.8rem;
    color: white;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .marker-confidence-badge {
    padding: 0.3rem 0.6rem;
    background: #e2e8f0;
    color: #4a5568;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .marker-position, .marker-description {
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    line-height: 1.4;
  }

  .no-markers {
    color: #64748b;
    font-style: italic;
  }

  .empty-detail {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    padding: 3rem 2rem;
    text-align: center;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

  .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .empty-detail h3 {
    color: #4a5568;
    margin-bottom: 0.5rem;
  }

  .empty-detail p {
    color: #64748b;
    line-height: 1.5;
  }
</style>