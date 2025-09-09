<script lang="ts">
  import { onMount } from 'svelte';
  
  export let systemStatus = 'ready';
  export let databaseConnected = false;
  export let constitutionalCompliance = 'LD-3.4-constitution';
  
  let currentTime = new Date();
  let analysisEngines = {
    ATO: { status: 'active', lastUpdate: '2s ago' },
    SEM: { status: 'active', lastUpdate: '1s ago' },
    CLU: { status: 'active', lastUpdate: '3s ago' },
    MEMA: { status: 'active', lastUpdate: '2s ago' }
  };
  
  let systemMetrics = {
    cpu: 12,
    memory: 24,
    storage: 67,
    network: 'offline'
  };
  
  let notifications = [
    { id: 1, type: 'info', message: 'System initialized successfully', timestamp: new Date() },
    { id: 2, type: 'success', message: 'Database connection established', timestamp: new Date(Date.now() - 30000) },
    { id: 3, type: 'info', message: 'Constitutional compliance verified', timestamp: new Date(Date.now() - 60000) }
  ];
  
  onMount(() => {
    const timeInterval = setInterval(() => {
      currentTime = new Date();
    }, 1000);
    
    return () => clearInterval(timeInterval);
  });
  
  function formatTime(date) {
    return date.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }
  
  function getStatusColor(status) {
    const colors = {
      'ready': '#38a169',
      'connected': '#38a169',
      'processing': '#667eea',
      'error': '#e53e3e',
      'warning': '#d69e2e'
    };
    return colors[status] || '#64748b';
  }
  
  function getEngineStatusColor(status) {
    const colors = {
      'active': '#38a169',
      'idle': '#d69e2e',
      'error': '#e53e3e'
    };
    return colors[status] || '#64748b';
  }
  
  function clearNotifications() {
    notifications = [];
  }
</script>

<div class="status-bar">
  <div class="status-section system-status">
    <div class="status-group">
      <div class="status-item">
        <span class="status-icon">⚡</span>
        <span class="status-text">System:</span>
        <span class="status-value" style="color: {getStatusColor(systemStatus)}">
          {systemStatus.toUpperCase()}
        </span>
      </div>
      
      <div class="status-item">
        <span class="status-icon">🔐</span>
        <span class="status-text">Database:</span>
        <span class="status-value" style="color: {getStatusColor(databaseConnected ? 'connected' : 'error')}">
          {databaseConnected ? 'CONNECTED' : 'DISCONNECTED'}
        </span>
      </div>
      
      <div class="status-item">
        <span class="status-icon">🏛️</span>
        <span class="status-text">Framework:</span>
        <span class="status-value" style="color: {getStatusColor('connected')}">
          {constitutionalCompliance.toUpperCase()}
        </span>
      </div>
    </div>
  </div>
  
  <div class="status-section analysis-engines">
    <div class="engines-header">
      <span class="section-icon">🎯</span>
      <span class="section-title">Analysis Engines</span>
    </div>
    <div class="engines-grid">
      {#each Object.entries(analysisEngines) as [engine, info]}
        <div class="engine-status">
          <span class="engine-name">{engine}</span>
          <div class="engine-indicator" style="background-color: {getEngineStatusColor(info.status)}"></div>
          <span class="engine-update">{info.lastUpdate}</span>
        </div>
      {/each}
    </div>
  </div>
  
  <div class="status-section system-metrics">
    <div class="metrics-header">
      <span class="section-icon">📊</span>
      <span class="section-title">System Metrics</span>
    </div>
    <div class="metrics-grid">
      <div class="metric-item">
        <span class="metric-label">CPU</span>
        <div class="metric-bar">
          <div class="metric-fill" style="width: {systemMetrics.cpu}%; background-color: {systemMetrics.cpu > 80 ? '#e53e3e' : systemMetrics.cpu > 60 ? '#d69e2e' : '#38a169'}"></div>
        </div>
        <span class="metric-value">{systemMetrics.cpu}%</span>
      </div>
      
      <div class="metric-item">
        <span class="metric-label">RAM</span>
        <div class="metric-bar">
          <div class="metric-fill" style="width: {systemMetrics.memory}%; background-color: {systemMetrics.memory > 80 ? '#e53e3e' : systemMetrics.memory > 60 ? '#d69e2e' : '#38a169'}"></div>
        </div>
        <span class="metric-value">{systemMetrics.memory}%</span>
      </div>
      
      <div class="metric-item">
        <span class="metric-label">Storage</span>
        <div class="metric-bar">
          <div class="metric-fill" style="width: {systemMetrics.storage}%; background-color: {systemMetrics.storage > 80 ? '#e53e3e' : systemMetrics.storage > 60 ? '#d69e2e' : '#38a169'}"></div>
        </div>
        <span class="metric-value">{systemMetrics.storage}%</span>
      </div>
      
      <div class="metric-item network">
        <span class="metric-label">Network</span>
        <span class="network-status offline">OFFLINE</span>
      </div>
    </div>
  </div>
  
  <div class="status-section notifications">
    <div class="notifications-header">
      <span class="section-icon">🔔</span>
      <span class="section-title">Notifications</span>
      <span class="notifications-count">{notifications.length}</span>
      {#if notifications.length > 0}
        <button class="clear-btn" on:click={clearNotifications}>Clear</button>
      {/if}
    </div>
    {#if notifications.length > 0}
      <div class="notifications-list">
        {#each notifications.slice(-3) as notification}
          <div class="notification-item {notification.type}">
            <span class="notification-icon">
              {notification.type === 'success' ? '✅' : notification.type === 'warning' ? '⚠️' : 'ℹ️'}
            </span>
            <span class="notification-message">{notification.message}</span>
          </div>
        {/each}
      </div>
    {:else}
      <div class="no-notifications">
        <span class="no-notifications-text">No notifications</span>
      </div>
    {/if}
  </div>
  
  <div class="status-section time-section">
    <div class="time-display">
      <span class="time-icon">🕒</span>
      <span class="current-time">{formatTime(currentTime)}</span>
    </div>
    <div class="offline-indicator">
      <span class="offline-icon">🔒</span>
      <span class="offline-text">OFFLINE MODE</span>
    </div>
  </div>
</div>

<style>
  .status-bar {
    display: flex;
    align-items: center;
    gap: 2rem;
    padding: 0.75rem 2rem;
    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
    color: white;
    font-size: 0.85rem;
    border-top: 1px solid #4a5568;
    overflow-x: auto;
  }

  .status-section {
    display: flex;
    align-items: center;
    gap: 1rem;
    white-space: nowrap;
  }

  .status-group {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .status-icon {
    font-size: 1rem;
  }

  .status-text {
    color: #a0aec0;
    font-weight: 500;
  }

  .status-value {
    font-weight: 600;
    font-size: 0.8rem;
  }

  .engines-header, .metrics-header, .notifications-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-right: 1rem;
  }

  .section-icon {
    font-size: 1rem;
  }

  .section-title {
    font-weight: 600;
    color: #e2e8f0;
  }

  .engines-grid {
    display: flex;
    gap: 1rem;
  }

  .engine-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.8rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
  }

  .engine-name {
    font-weight: 600;
    font-size: 0.8rem;
  }

  .engine-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  .engine-update {
    font-size: 0.7rem;
    color: #a0aec0;
  }

  .metrics-grid {
    display: flex;
    gap: 1rem;
  }

  .metric-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .metric-item.network {
    gap: 0.5rem;
  }

  .metric-label {
    font-size: 0.8rem;
    color: #a0aec0;
    min-width: 50px;
  }

  .metric-bar {
    width: 60px;
    height: 6px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
    overflow: hidden;
  }

  .metric-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
  }

  .metric-value {
    font-size: 0.8rem;
    font-weight: 600;
    min-width: 35px;
    text-align: right;
  }

  .network-status {
    padding: 0.2rem 0.6rem;
    border-radius: 10px;
    font-size: 0.7rem;
    font-weight: 600;
  }

  .network-status.offline {
    background: #38a169;
    color: white;
  }

  .notifications-count {
    padding: 0.2rem 0.5rem;
    background: #667eea;
    color: white;
    border-radius: 10px;
    font-size: 0.7rem;
    font-weight: 600;
    min-width: 20px;
    text-align: center;
  }

  .clear-btn {
    padding: 0.2rem 0.6rem;
    background: transparent;
    border: 1px solid #4a5568;
    color: #a0aec0;
    border-radius: 8px;
    font-size: 0.7rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .clear-btn:hover {
    background: #4a5568;
    color: white;
  }

  .notifications-list {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    max-width: 300px;
  }

  .notification-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.3rem 0.6rem;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.1);
  }

  .notification-item.success {
    background: rgba(56, 161, 105, 0.2);
  }

  .notification-item.warning {
    background: rgba(214, 158, 46, 0.2);
  }

  .notification-item.info {
    background: rgba(102, 126, 234, 0.2);
  }

  .notification-icon {
    font-size: 0.8rem;
  }

  .notification-message {
    font-size: 0.8rem;
    color: #e2e8f0;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .no-notifications {
    padding: 0.5rem;
  }

  .no-notifications-text {
    color: #a0aec0;
    font-size: 0.8rem;
    font-style: italic;
  }

  .time-section {
    margin-left: auto;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    align-items: flex-end;
  }

  .time-display {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .time-icon {
    font-size: 1rem;
  }

  .current-time {
    font-family: monospace;
    font-weight: 600;
    font-size: 0.9rem;
    color: #e2e8f0;
  }

  .offline-indicator {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .offline-icon {
    font-size: 0.8rem;
  }

  .offline-text {
    font-size: 0.7rem;
    color: #38a169;
    font-weight: 600;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.6;
    }
  }

  /* Mobile responsiveness */
  @media (max-width: 1200px) {
    .status-bar {
      gap: 1rem;
      padding: 0.75rem 1rem;
    }
    
    .status-section {
      gap: 0.75rem;
    }
    
    .engines-grid, .metrics-grid {
      gap: 0.75rem;
    }
  }
</style>