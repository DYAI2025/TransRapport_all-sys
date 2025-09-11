<script lang="ts">
import { onMount } from 'svelte';
import { invoke } from '@tauri-apps/api/core';

let message = 'Loading...';

onMount(async () => {
try {
// Test Tauri IPC
message = await invoke('greet', { name: 'TransRapport' });
} catch (error) {
message = 'Tauri not available - running in browser mode';
console.log('Tauri error:', error);
}
});
</script>

<main class="min-h-screen bg-gray-900 text-white p-8">
<div class="max-w-4xl mx-auto">
<h1 class="text-4xl font-bold mb-8 text-center">
TransRapport Hybrid
</h1>

<div class="bg-gray-800 rounded-lg p-6 mb-8">
<h2 class="text-2xl font-semibold mb-4">System Status</h2>
<p class="text-gray-300">{message}</p>
</div>

<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
<a href="/capture" class="bg-blue-600 hover:bg-blue-700 p-6 rounded-lg transition-colors">
<h3 class="text-xl font-semibold mb-2">🎤 Capture</h3>
<p class="text-blue-100">Record and analyze audio in real-time</p>
</a>

<a href="/explore" class="bg-green-600 hover:bg-green-700 p-6 rounded-lg transition-colors">
<h3 class="text-xl font-semibold mb-2">🔍 Explore</h3>
<p class="text-green-100">Analyze recorded sessions and markers</p>
</a>

<a href="/perform" class="bg-purple-600 hover:bg-purple-700 p-6 rounded-lg transition-colors">
<h3 class="text-xl font-semibold mb-2">🎭 Perform</h3>
<p class="text-purple-100">Live performance with overlays</p>
</a>
</div>
</div>
</main>
