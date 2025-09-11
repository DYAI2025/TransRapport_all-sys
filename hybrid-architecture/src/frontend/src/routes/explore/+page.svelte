<script lang="ts">
+page.svelte import { onMount } from 'svelte';

+page.svelte let sessions: any[] = [];
+page.svelte let selectedSession: any = null;
+page.svelte let timelineZoom = 1;

+page.svelte // Mock data for demonstration
+page.svelte onMount(() => {
+page.svelte +page.svelte sessions = [
+page.svelte +page.svelte +page.svelte {
+page.svelte +page.svelte +page.svelte +page.svelte id: 1,
+page.svelte +page.svelte +page.svelte +page.svelte name: 'Morning Meeting',
+page.svelte +page.svelte +page.svelte +page.svelte duration: '45:32',
+page.svelte +page.svelte +page.svelte +page.svelte markers: 23,
+page.svelte +page.svelte +page.svelte +page.svelte date: '2024-01-15',
+page.svelte +page.svelte +page.svelte +page.svelte thumbnail: '/api/placeholder/200/100'
+page.svelte +page.svelte +page.svelte },
+page.svelte +page.svelte +page.svelte {
+page.svelte +page.svelte +page.svelte +page.svelte id: 2,
+page.svelte +page.svelte +page.svelte +page.svelte name: 'Podcast Recording',
+page.svelte +page.svelte +page.svelte +page.svelte duration: '1:23:15',
+page.svelte +page.svelte +page.svelte +page.svelte markers: 67,
+page.svelte +page.svelte +page.svelte +page.svelte date: '2024-01-14',
+page.svelte +page.svelte +page.svelte +page.svelte thumbnail: '/api/placeholder/200/100'
+page.svelte +page.svelte +page.svelte }
+page.svelte +page.svelte ];
+page.svelte });

+page.svelte function selectSession(session: any) {
+page.svelte +page.svelte selectedSession = session;
+page.svelte }
</script>

<main class="min-h-screen bg-gray-900 text-white p-8">
+page.svelte <div class="max-w-6xl mx-auto">
+page.svelte +page.svelte <!-- Header -->
+page.svelte +page.svelte <div class="flex justify-between items-center mb-8">
+page.svelte +page.svelte +page.svelte <h1 class="text-3xl font-bold">🔍 Explore Mode</h1>
+page.svelte +page.svelte +page.svelte <a href="/" class="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors">
+page.svelte +page.svelte +page.svelte +page.svelte ← Back to Home
+page.svelte +page.svelte +page.svelte </a>
+page.svelte +page.svelte </div>

+page.svelte +page.svelte <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
+page.svelte +page.svelte +page.svelte <!-- Sessions List -->
+page.svelte +page.svelte +page.svelte <div class="lg:col-span-1">
+page.svelte +page.svelte +page.svelte +page.svelte <div class="bg-gray-800 rounded-lg p-6">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <h2 class="text-xl font-semibold mb-4">Recorded Sessions</h2>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="space-y-3">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {#each sessions as session}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte class="bg-gray-700 rounded-lg p-4 cursor-pointer hover:bg-gray-600 transition-colors {selectedSession?.id === session.id ? 'ring-2 ring-blue-500' : ''}"
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte on:click={() => selectSession(session)}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte >
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <h3 class="font-semibold mb-1">{session.name}</h3>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="text-sm text-gray-300 space-y-1">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div>Duration: {session.duration}</div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div>Markers: {session.markers}</div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div>Date: {session.date}</div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {/each}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>

+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {#if sessions.length === 0}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="text-center text-gray-400 py-8">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte No recorded sessions yet.<br>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <a href="/capture" class="text-blue-400 hover:text-blue-300">Start recording →</a>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {/if}
+page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte </div>

+page.svelte +page.svelte +page.svelte <!-- Timeline & Analysis -->
+page.svelte +page.svelte +page.svelte <div class="lg:col-span-2">
+page.svelte +page.svelte +page.svelte +page.svelte {#if selectedSession}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="space-y-6">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <!-- Session Info -->
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="bg-gray-800 rounded-lg p-6">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <h2 class="text-xl font-semibold mb-4">{selectedSession.name}</h2>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-gray-400">Duration:</span><br>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="font-semibold">{selectedSession.duration}</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-gray-400">Markers:</span><br>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="font-semibold">{selectedSession.markers}</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-gray-400">Date:</span><br>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="font-semibold">{selectedSession.date}</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-gray-400">Quality:</span><br>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="font-semibold text-green-400">Good</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>

+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <!-- Timeline Controls -->
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="bg-gray-800 rounded-lg p-6">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="flex justify-between items-center mb-4">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <h3 class="text-lg font-semibold">Timeline Analysis</h3>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="flex items-center space-x-4">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <button class="bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded text-sm">Zoom In</button>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-sm text-gray-400">Zoom: {timelineZoom}x</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <button class="bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded text-sm">Zoom Out</button>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <!-- Timeline Visualization -->
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="bg-gray-700 rounded-lg p-4 mb-4">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="h-64 flex items-center justify-center">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-gray-400">Interactive timeline will appear here</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>

+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <!-- Marker Layers -->
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="space-y-2">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <h4 class="font-semibold mb-2">Marker Layers</h4>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="space-y-1">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <label class="flex items-center space-x-2">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <input type="checkbox" checked class="rounded">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-sm">Pitch Changes (f0)</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </label>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <label class="flex items-center space-x-2">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <input type="checkbox" checked class="rounded">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-sm">Volume Peaks (RMS)</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </label>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <label class="flex items-center space-x-2">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <input type="checkbox" checked class="rounded">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-sm">Pauses</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </label>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <label class="flex items-center space-x-2">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <input type="checkbox" class="rounded">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-sm">Speaker Changes</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </label>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>

+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <!-- Export Options -->
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="bg-gray-800 rounded-lg p-6">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <h3 class="text-lg font-semibold mb-4">Export & Analysis</h3>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <button class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition-colors">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte 📊 Export CSV
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </button>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <button class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-semibold transition-colors">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte 🎵 Export Audio
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </button>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <button class="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-semibold transition-colors">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte 📈 Generate Report
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </button>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte {:else}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="bg-gray-800 rounded-lg p-12 text-center">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="text-6xl mb-4">🔍</div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <h3 class="text-xl font-semibold mb-2">Select a Session</h3>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <p class="text-gray-400">Choose a recorded session from the list to explore its analysis</p>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte {/if}
+page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte </div>
+page.svelte </div>
</main>
