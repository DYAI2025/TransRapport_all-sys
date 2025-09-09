<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  // Demo conversation data (in production, this would come from the backend)
  let conversations = [
    {
      id: 'edff3e4f-52ac-4f46-83bf-c3b133a6f69e',
      name: 'Demo Analysis Session',
      description: 'Constitutional marker analysis demo',
      created_at: '2025-09-09T04:32:43.877676',
      status: 'completed',
      stats: {
        segments: 14,
        markers: 1,
        duration: 65.5,
        rapport_avg: 0.0,
        constitutional_compliance: 'VERIFIED'
      },
      markers_summary: {
        'CLU': 1,
        'ATO': 0,
        'SEM': 0,
        'MEMA': 0
      }
    },
    {
      id: 'demo-session-2',
      name: 'Q4 Strategy Meeting',
      description: 'Executive team quarterly planning session',
      created_at: '2025-09-08T14:15:30.000000',
      status: 'completed',
      stats: {
        segments: 32,
        markers: 8,
        duration: 145.2,
        rapport_avg: 0.74,
        constitutional_compliance: 'VERIFIED'
      },
      markers_summary: {
        'CLU': 3,
        'ATO': 2,
        'SEM': 2,
        'MEMA': 1
      }
    },
    {
      id: 'demo-session-3',
      name: 'Product Review Session',
      description: 'Cross-functional product planning',
      created_at: '2025-09-07T10:30:15.000000',
      status: 'completed',
      stats: {
        segments: 28,
        markers: 12,
        duration: 198.7,
        rapport_avg: 0.68,
        constitutional_compliance: 'VERIFIED'
      },
      markers_summary: {
        'CLU': 4,
        'ATO': 3,
        'SEM': 3,
        'MEMA': 2
      }
    }
  ];
  
  let searchTerm = '';
  let selectedConversation = null;
  
  $: filteredConversations = conversations.filter(conv =>
    conv.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.description.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  function selectConversation(conversation) {
    selectedConversation = conversation;
    dispatch('conversationselect', { conversation });
  }
  
  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }
  
  onMount(() => {
    console.log('ConversationList mounted with', conversations.length, 'conversations');
  });
</script>

<div class="conversation-list">
  <div class="list-header">
    <h2 class="list-title">
      <span class="title-icon">💬</span>
      Conversation Sessions
    </h2>
    <p class="list-subtitle">Constitutional analysis sessions with LD-3.4 compliance</p>
    
    <div class="search-bar">
      <input
        type="text"
        placeholder="Search conversations..."
        bind:value={searchTerm}
        class="search-input"
      />
      <span class="search-icon">🔍</span>
    </div>
  </div>

  <div class="conversations-grid">
    {#each filteredConversations as conversation}
      <div 
        class="conversation-card"
        class:selected={selectedConversation?.id === conversation.id}
        on:click={() => selectConversation(conversation)}
        role="button"
        tabindex="0"
      >
        <div class="card-header">
          <div class="conversation-info">
            <h3 class="conversation-name">{conversation.name}</h3>
            <p class="conversation-description">{conversation.description}</p>
          </div>
          <div class="status-badge {conversation.status}">
            {conversation.status}
          </div>
        </div>
        
        <div class="card-body">
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{conversation.stats.segments}</span>
              <span class="stat-label">Segments</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{conversation.stats.markers}</span>
              <span class="stat-label">Markers</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{formatDuration(conversation.stats.duration)}</span>
              <span class="stat-label">Duration</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{conversation.stats.rapport_avg.toFixed(2)}</span>
              <span class="stat-label">Rapport</span>
            </div>
          </div>
          
          <div class="markers-summary">
            <div class="markers-title">Constitutional Markers:</div>
            <div class="markers-breakdown">
              {#each Object.entries(conversation.markers_summary) as [type, count]}
                {#if count > 0}
                  <span class="marker-badge {type.toLowerCase()}">
                    {type}: {count}
                  </span>
                {/if}
              {/each}
            </div>
          </div>
        </div>
        
        <div class="card-footer">
          <div class="compliance-indicator">
            <span class="compliance-icon">🏛️</span>
            <span class="compliance-text">{conversation.stats.constitutional_compliance}</span>
          </div>
          <div class="timestamp">
            {formatDate(conversation.created_at)}
          </div>
        </div>
      </div>
    {/each}
  </div>
  
  {#if filteredConversations.length === 0}
    <div class="empty-state">
      <span class="empty-icon">📝</span>
      <h3>No conversations found</h3>
      <p>Start a new constitutional analysis session to see results here.</p>
      <button class="create-button">
        <span class="button-icon">🆕</span>
        Create New Session
      </button>
    </div>
  {/if}
</div>

<style>
  .conversation-list {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .list-header {
    margin-bottom: 2rem;
  }

  .list-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 2rem;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 0.5rem;
  }

  .title-icon {
    font-size: 2.2rem;
  }

  .list-subtitle {
    color: #64748b;
    margin-bottom: 2rem;
    font-size: 1.1rem;
  }

  .search-bar {
    position: relative;
    max-width: 400px;
  }

  .search-input {
    width: 100%;
    padding: 1rem 3rem 1rem 1rem;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    font-size: 1rem;
    transition: all 0.2s ease;
  }

  .search-input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  .search-icon {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.2rem;
    color: #64748b;
  }

  .conversations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 1.5rem;
    flex: 1;
  }

  .conversation-card {
    background: white;
    border-radius: 12px;
    border: 2px solid #e2e8f0;
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .conversation-card:hover {
    border-color: #667eea;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    transform: translateY(-2px);
  }

  .conversation-card.selected {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    background: linear-gradient(135deg, #f8faff 0%, #f1f5ff 100%);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
  }

  .conversation-info {
    flex: 1;
  }

  .conversation-name {
    font-size: 1.2rem;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 0.5rem;
  }

  .conversation-description {
    color: #64748b;
    font-size: 0.9rem;
    line-height: 1.4;
    margin: 0;
  }

  .status-badge {
    padding: 0.4rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .status-badge.completed {
    background: #c6f6d5;
    color: #22543d;
  }

  .status-badge.pending {
    background: #fef3c7;
    color: #92400e;
  }

  .card-body {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
  }

  .stat-item {
    text-align: center;
    padding: 0.75rem;
    background: #f8fafc;
    border-radius: 8px;
  }

  .stat-value {
    display: block;
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

  .markers-summary {
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
  }

  .markers-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 0.75rem;
  }

  .markers-breakdown {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .marker-badge {
    padding: 0.3rem 0.7rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    color: white;
  }

  .marker-badge.ato {
    background: #667eea;
  }

  .marker-badge.sem {
    background: #764ba2;
  }

  .marker-badge.clu {
    background: #f093fb;
  }

  .marker-badge.mema {
    background: #4facfe;
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1rem;
    border-top: 1px solid #e2e8f0;
  }

  .compliance-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    font-weight: 600;
    color: #38a169;
  }

  .compliance-icon {
    font-size: 1.1rem;
  }

  .timestamp {
    font-size: 0.8rem;
    color: #64748b;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
    color: #64748b;
  }

  .empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
  }

  .empty-state h3 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    color: #4a5568;
  }

  .empty-state p {
    font-size: 1rem;
    margin-bottom: 2rem;
  }

  .create-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .create-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }

  .button-icon {
    font-size: 1.2rem;
  }
</style>