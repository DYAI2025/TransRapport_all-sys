<script lang="ts">
+page.svelte import { onMount } from 'svelte';

+page.svelte let isLive = false;
+page.svelte let selectedPreset = 'Default';
+page.svelte let overlayOpacity = 0.8;
+page.svelte let showMarkers = true;
+page.svelte let showSpeakerRibbon = true;

+page.svelte const presets = [
+page.svelte +page.svelte { name: 'Default', description: 'Standard overlay settings' },
+page.svelte +page.svelte { name: 'Podcast', description: 'Optimized for podcast recording' },
+page.svelte +page.svelte { name: 'Theater', description: 'Stage performance with cues' },
+page.svelte +page.svelte { name: 'Meeting', description: 'Professional meeting overlay' }
+page.svelte ];

+page.svelte function toggleLive() {
+page.svelte +page.svelte isLive = !isLive;
+page.svelte }

+page.svelte function selectPreset(presetName: string) {
+page.svelte +page.svelte selectedPreset = presetName;
+page.svelte +page.svelte // TODO: Load preset configuration
+page.svelte }
</script>

<main class="min-h-screen bg-gray-900 text-white p-8">
+page.svelte <div class="max-w-6xl mx-auto">
+page.svelte +page.svelte <!-- Header -->
+page.svelte +page.svelte <div class="flex justify-between items-center mb-8">
+page.svelte +page.svelte +page.svelte <h1 class="text-3xl font-bold">🎭 Perform Mode</h1>
+page.svelte +page.svelte +page.svelte <a href="/" class="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors">
+page.svelte +page.svelte +page.svelte +page.svelte ← Back to Home
+page.svelte +page.svelte +page.svelte </a>
+page.svelte +page.svelte </div>

+page.svelte +page.svelte <!-- Live Controls -->
+page.svelte +page.svelte <div class="bg-gray-800 rounded-lg p-6 mb-6">
+page.svelte +page.svelte +page.svelte <div class="flex justify-between items-center mb-6">
+page.svelte +page.svelte +page.svelte +page.svelte <h2 class="text-xl font-semibold">Live Performance Controls</h2>
+page.svelte +page.svelte +page.svelte +page.svelte <div class="flex items-center space-x-4">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class={`text-lg ${isLive ? 'text-red-400' : 'text-gray-400'}`}>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {isLive ? '🔴 LIVE' : '⚫ OFFLINE'}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <button 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte on:click={toggleLive}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte class={`px-6 py-3 rounded-lg font-semibold transition-colors ${
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte isLive 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte ? 'bg-red-600 hover:bg-red-700' 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte : 'bg-green-600 hover:bg-green-700'
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte }`}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte >
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {isLive ? 'Stop Live' : 'Go Live'}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </button>
+page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte </div>

+page.svelte +page.svelte +page.svelte <!-- Preset Selection -->
+page.svelte +page.svelte +page.svelte <div class="mb-6">
+page.svelte +page.svelte +page.svelte +page.svelte <h3 class="font-semibold mb-3">Performance Preset</h3>
+page.svelte +page.svelte +page.svelte +page.svelte <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {#each presets as preset}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <button 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte on:click={() => selectPreset(preset.name)}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte class={`p-3 rounded-lg border-2 transition-colors ${
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte selectedPreset === preset.name 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte ? 'border-blue-500 bg-blue-500/20' 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte : 'border-gray-600 hover:border-gray-500'
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte }`}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte >
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="font-semibold">{preset.name}</div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="text-xs text-gray-400 mt-1">{preset.description}</div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </button>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {/each}
+page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte </div>

+page.svelte +page.svelte +page.svelte <!-- Overlay Settings -->
+page.svelte +page.svelte +page.svelte <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
+page.svelte +page.svelte +page.svelte +page.svelte <div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <label class="block text-sm font-medium mb-2">Overlay Opacity</label>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <input 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte type="range" 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte min="0.1" 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte max="1" 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte step="0.1" 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte bind:value={overlayOpacity}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte class="w-full"
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte >
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="text-center text-sm text-gray-400 mt-1">{Math.round(overlayOpacity * 100)}%</div>
+page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte 
+page.svelte +page.svelte +page.svelte +page.svelte <div class="flex items-center space-x-3">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <input 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte type="checkbox" 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte id="showMarkers" 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte bind:checked={showMarkers}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte class="rounded"
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte >
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <label for="showMarkers" class="text-sm font-medium">Show Marker Badges</label>
+page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte 
+page.svelte +page.svelte +page.svelte +page.svelte <div class="flex items-center space-x-3">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <input 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte type="checkbox" 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte id="showSpeakerRibbon" 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte bind:checked={showSpeakerRibbon}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte class="rounded"
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte >
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <label for="showSpeakerRibbon" class="text-sm font-medium">Show Speaker Ribbon</label>
+page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte </div>

+page.svelte +page.svelte <!-- Live Overlay Preview -->
+page.svelte +page.svelte <div class="bg-gray-800 rounded-lg p-6 mb-6">
+page.svelte +page.svelte +page.svelte <h2 class="text-xl font-semibold mb-4">Live Overlay Preview</h2>
+page.svelte +page.svelte +page.svelte 
+page.svelte +page.svelte +page.svelte <div class="relative bg-black rounded-lg overflow-hidden" style="aspect-ratio: 16/9;">
+page.svelte +page.svelte +page.svelte +page.svelte <!-- Mock video feed -->
+page.svelte +page.svelte +page.svelte +page.svelte <div class="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="text-center">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="text-6xl mb-4">📹</div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <p class="text-gray-400">Live video feed will appear here</p>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <p class="text-sm text-gray-500 mt-2">Connect camera for live performance</p>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte </div>

+page.svelte +page.svelte +page.svelte +page.svelte <!-- Performance Overlay (conditionally rendered) -->
+page.svelte +page.svelte +page.svelte +page.svelte {#if isLive}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div 
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte class="absolute inset-0 pointer-events-none"
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte style="opacity: {overlayOpacity}"
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte >
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <!-- Marker Badges -->
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {#if showMarkers}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="absolute top-4 left-4 space-y-2">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte Pitch ↑ 220Hz
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="bg-green-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte Volume ↑ -12dB
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="bg-yellow-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte Pause 2.3s
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {/if}

+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <!-- Speaker Ribbon -->
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {#if showSpeakerRibbon}
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="absolute bottom-4 left-4 right-4">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="bg-black/50 backdrop-blur-sm rounded-lg p-3">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="flex items-center space-x-4">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="flex items-center space-x-2">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="w-3 h-3 bg-green-500 rounded-full"></div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-white text-sm font-semibold">Speaker 1</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="flex-1 bg-gray-700 rounded-full h-2">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="bg-blue-500 h-2 rounded-full" style="width: 75%"></div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <span class="text-white text-sm">75%</span>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte {/if}

+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <!-- Performance Metrics -->
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-lg p-3">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div class="text-xs text-white space-y-1">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div>Latency: 45ms</div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div>CPU: 28%</div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte <div>Markers: 12 active</div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte +page.svelte +page.svelte {/if}
+page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte </div>

+page.svelte +page.svelte <!-- Quick Actions -->
+page.svelte +page.svelte <div class="bg-gray-800 rounded-lg p-6">
+page.svelte +page.svelte +page.svelte <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
+page.svelte +page.svelte +page.svelte <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
+page.svelte +page.svelte +page.svelte +page.svelte <button class="bg-red-600 hover:bg-red-700 p-4 rounded-lg font-semibold transition-colors">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte 🎬 Record Session
+page.svelte +page.svelte +page.svelte +page.svelte </button>
+page.svelte +page.svelte +page.svelte +page.svelte <button class="bg-blue-600 hover:bg-blue-700 p-4 rounded-lg font-semibold transition-colors">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte 📸 Take Screenshot
+page.svelte +page.svelte +page.svelte +page.svelte </button>
+page.svelte +page.svelte +page.svelte +page.svelte <button class="bg-green-600 hover:bg-green-700 p-4 rounded-lg font-semibold transition-colors">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte 💾 Save Preset
+page.svelte +page.svelte +page.svelte +page.svelte </button>
+page.svelte +page.svelte +page.svelte +page.svelte <button class="bg-purple-600 hover:bg-purple-700 p-4 rounded-lg font-semibold transition-colors">
+page.svelte +page.svelte +page.svelte +page.svelte +page.svelte ⚙️ Advanced Settings
+page.svelte +page.svelte +page.svelte +page.svelte </button>
+page.svelte +page.svelte +page.svelte </div>
+page.svelte +page.svelte </div>
+page.svelte </div>
</main>
