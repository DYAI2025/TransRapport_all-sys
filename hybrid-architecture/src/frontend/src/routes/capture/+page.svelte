<script lang="ts">
import { onMount } from 'svelte';
import { invoke } from '@tauri-apps/api/core';

let isRecording = false;
let audioDevices: string[] = [];
let selectedDevice = '';
let status = 'Ready to record';

async function startRecording() {
try {
isRecording = true;
status = 'Recording...';
// TODO: Implement actual recording via Tauri
await invoke('start_recording', { device: selectedDevice });
} catch (error) {
status = 'Error starting recording';
console.error('Recording error:', error);
}
}

async function stopRecording() {
try {
isRecording = false;
status = 'Processing...';
// TODO: Implement stop recording
await invoke('stop_recording');
status = 'Recording saved';
} catch (error) {
status = 'Error stopping recording';
console.error('Stop recording error:', error);
}
}

onMount(async () => {
try {
// TODO: Get available audio devices
audioDevices = await invoke('get_audio_devices') || ['Default Device'];
selectedDevice = audioDevices[0];
} catch (error) {
console.log('Audio devices not available:', error);
audioDevices = ['Default Device'];
selectedDevice = 'Default Device';
}
});
</script>

<main class="min-h-screen bg-gray-900 text-white p-8">
<div class="max-w-6xl mx-auto">
<!-- Header -->
<div class="flex justify-between items-center mb-8">
<h1 class="text-3xl font-bold">🎤 Capture Mode</h1>
<a href="/" class="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors">
← Back to Home
</a>
</div>

<!-- Status Bar -->
<div class="bg-gray-800 rounded-lg p-4 mb-6">
<div class="flex justify-between items-center">
<span class="text-gray-300">Status: {status}</span>
<div class="flex items-center space-x-4">
<span class="text-green-400">● CPU: 15%</span>
<span class="text-blue-400">● RAM: 120MB</span>
<span class="text-yellow-400">● Latency: 45ms</span>
</div>
</div>
</div>

<!-- Controls -->
<div class="bg-gray-800 rounded-lg p-6 mb-6">
<h2 class="text-xl font-semibold mb-4">Recording Controls</h2>

<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
<div>
<label class="block text-sm font-medium mb-2">Audio Device</label>
<select 
bind:value={selectedDevice} 
class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2"
>
{#each audioDevices as device}
<option value={device}>{device}</option>
{/each}
</select>
</div>

<div>
<label class="block text-sm font-medium mb-2">Session Name</label>
<input 
type="text" 
placeholder="My Recording Session"
class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2"
>
</div>
</div>

<div class="flex space-x-4">
{#if !isRecording}
<button 
on:click={startRecording}
class="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-lg font-semibold transition-colors"
>
▶️ Start Recording
</button>
{:else}
<button 
on:click={stopRecording}
class="bg-gray-600 hover:bg-gray-500 px-6 py-3 rounded-lg font-semibold transition-colors"
>
⏹️ Stop Recording
</button>
{/if}

<button class="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition-colors">
💾 Save Session
</button>
</div>
</div>

<!-- Live Visualization -->
<div class="bg-gray-800 rounded-lg p-6 mb-6">
<h2 class="text-xl font-semibold mb-4">Live Audio Analysis</h2>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
<!-- Waveform -->
<div class="bg-gray-700 rounded-lg p-4">
<h3 class="font-semibold mb-2">Waveform</h3>
<div class="h-32 bg-gray-600 rounded flex items-center justify-center">
<span class="text-gray-400">Waveform visualization</span>
</div>
</div>

<!-- Prosody -->
<div class="bg-gray-700 rounded-lg p-4">
<h3 class="font-semibold mb-2">Prosody (f0, RMS)</h3>
<div class="space-y-2">
<div class="flex justify-between">
<span>Pitch (f0):</span>
<span class="text-blue-400">-- Hz</span>
</div>
<div class="flex justify-between">
<span>Volume (RMS):</span>
<span class="text-green-400">-- dB</span>
</div>
<div class="flex justify-between">
<span>Pause Duration:</span>
<span class="text-yellow-400">-- ms</span>
</div>
</div>
</div>

<!-- Markers -->
<div class="bg-gray-700 rounded-lg p-4">
<h3 class="font-semibold mb-2">Detected Markers</h3>
<div class="space-y-1">
<div class="text-gray-400 text-sm">No markers detected yet</div>
</div>
</div>
</div>
</div>

<!-- Timeline -->
<div class="bg-gray-800 rounded-lg p-6">
<h2 class="text-xl font-semibold mb-4">Recording Timeline</h2>
<div class="h-48 bg-gray-700 rounded flex items-center justify-center">
<span class="text-gray-400">Timeline will appear here during recording</span>
</div>
</div>
</div>
</main>
