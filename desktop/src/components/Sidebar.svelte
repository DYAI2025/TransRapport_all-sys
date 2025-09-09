<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  
  export let currentView = 'conversations';
  
  const dispatch = createEventDispatcher();
  
  const menuItems = [
    {
      id: 'conversations',
      icon: '💬',
      label: 'Conversations',
      description: 'View all analysis sessions'
    },
    {
      id: 'realtime',
      icon: '🎙️',
      label: 'Live Analysis',
      description: 'Real-time constitutional analysis'
    },
    {
      id: 'constitutional',
      icon: '🏛️',
      label: 'Constitutional',
      description: 'Framework compliance status'
    },
    {
      id: 'exports',
      icon: '📤',
      label: 'Exports',
      description: 'Generated reports and data'
    },
    {
      id: 'settings',
      icon: '⚙️',
      label: 'Settings',
      description: 'System configuration'
    }
  ];
  
  function selectView(viewId: string) {
    dispatch('viewchange', { view: viewId });
  }
</script>

<nav class="sidebar">
  <div class="nav-section">
    <h3 class="section-title">Navigation</h3>
    <ul class="menu-list">
      {#each menuItems as item}
        <li>
          <button
            class="menu-item"
            class:active={currentView === item.id}
            on:click={() => selectView(item.id)}
          >
            <span class="menu-icon">{item.icon}</span>
            <div class="menu-content">
              <span class="menu-label">{item.label}</span>
              <span class="menu-description">{item.description}</span>
            </div>
          </button>
        </li>
      {/each}
    </ul>
  </div>
  
  <div class="nav-section">
    <h3 class="section-title">Analysis Engines</h3>
    <div class="engine-status">
      <div class="engine" data-tooltip="Attention markers">
        <span class="engine-icon">🎯</span>
        <span class="engine-label">ATO</span>
        <span class="engine-status-dot active"></span>
      </div>
      <div class="engine" data-tooltip="Semantic markers">
        <span class="engine-icon">🧠</span>
        <span class="engine-label">SEM</span>
        <span class="engine-status-dot active"></span>
      </div>
      <div class="engine" data-tooltip="Cluster markers">
        <span class="engine-icon">🤝</span>
        <span class="engine-label">CLU</span>
        <span class="engine-status-dot active"></span>
      </div>
      <div class="engine" data-tooltip="Memory markers">
        <span class="engine-icon">🧮</span>
        <span class="engine-label">MEMA</span>
        <span class="engine-status-dot active"></span>
      </div>
    </div>
  </div>
  
  <div class="nav-section">
    <h3 class="section-title">Quick Actions</h3>
    <div class="quick-actions">
      <button class="quick-action">
        <span class="action-icon">🆕</span>
        <span class="action-label">New Session</span>
      </button>
      <button class="quick-action">
        <span class="action-icon">📊</span>
        <span class="action-label">Generate Report</span>
      </button>
      <button class="quick-action">
        <span class="action-icon">🔄</span>
        <span class="action-label">Sync Data</span>
      </button>
    </div>
  </div>
</nav>

<style>
  .sidebar {
    width: 280px;
    background: #1a202c;
    color: white;
    padding: 1.5rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .nav-section {
    border-bottom: 1px solid #2d3748;
    padding-bottom: 1.5rem;
  }

  .nav-section:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  .section-title {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    color: #a0aec0;
    margin-bottom: 1rem;
    letter-spacing: 0.5px;
  }

  .menu-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .menu-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border: none;
    background: transparent;
    color: #cbd5e0;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    width: 100%;
    text-align: left;
  }

  .menu-item:hover {
    background: #2d3748;
    color: white;
  }

  .menu-item.active {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }

  .menu-icon {
    font-size: 1.5rem;
    min-width: 24px;
  }

  .menu-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .menu-label {
    font-weight: 600;
    font-size: 0.95rem;
  }

  .menu-description {
    font-size: 0.8rem;
    opacity: 0.7;
  }

  .engine-status {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }

  .engine {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    background: #2d3748;
    border-radius: 6px;
    position: relative;
  }

  .engine-icon {
    font-size: 1.2rem;
  }

  .engine-label {
    font-size: 0.8rem;
    font-weight: 600;
  }

  .engine-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #68d391;
    margin-left: auto;
    box-shadow: 0 0 10px rgba(104, 211, 145, 0.6);
  }

  .engine-status-dot.active {
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.6;
    }
  }

  .quick-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .quick-action {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border: none;
    background: #2d3748;
    color: #cbd5e0;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.9rem;
  }

  .quick-action:hover {
    background: #4a5568;
    color: white;
    transform: translateY(-1px);
  }

  .action-icon {
    font-size: 1.1rem;
  }

  .action-label {
    font-weight: 500;
  }

  /* Tooltip styles */
  .engine[data-tooltip]:hover::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background: #1a202c;
    color: white;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    white-space: nowrap;
    z-index: 1000;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
  }
</style>