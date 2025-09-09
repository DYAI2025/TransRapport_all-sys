<script lang="ts">
  import { onMount } from 'svelte';
  import TransRapportWorkflow from './components/TransRapportWorkflow.svelte';
  
  let appReady = false;
  
  onMount(async () => {
    // Initialize application
    console.log('TransRapport Desktop Application starting...');
    appReady = true;
  });
</script>

<main class="app">
  {#if appReady}
    <TransRapportWorkflow />
  {:else}
    <div class="loading">
      <h1>TransRapport</h1>
      <p>Loading offline transcription system...</p>
    </div>
  {/if}
</main>

<style>
  .app {
    width: 100vw;
    height: 100vh;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .loading {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    color: white;
  }
  
  .loading h1 {
    font-size: 3em;
    margin-bottom: 1em;
    font-weight: 300;
  }
  
  .loading p {
    font-size: 1.2em;
    opacity: 0.8;
  }
</style>