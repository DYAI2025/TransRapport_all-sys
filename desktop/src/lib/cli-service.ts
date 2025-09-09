/**
 * CLI Service - Offline CLI interface using Tauri shell API only
 * NO HTTP, NO NETWORK - Child process spawning only
 */

import { Command } from '@tauri-apps/api/shell';

export interface CLIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  stdout?: string;
  stderr?: string;
}

export interface SessionInfo {
  id: string;
  name: string;
  status: 'idle' | 'recording' | 'processing' | 'completed';
  created: string;
  duration?: number;
  files: {
    raw_audio?: string;
    transcript?: string;
    diarization?: string;
    analysis?: string;
  };
}

export interface AudioDevice {
  id: string;
  name: string;
  is_default: boolean;
  max_input_channels: number;
  default_sample_rate: number;
}

export interface TranscriptionResult {
  text: string;
  language: string;
  duration: number;
  segments: Array<{
    id: string;
    start: number;
    end: number;
    text: string;
    confidence: number;
  }>;
}

export interface DiarizationResult {
  speakers: Array<{
    id: string;
    label: string;
    speaking_time: number;
    segment_count: number;
    average_confidence: number;
  }>;
  segments: Array<{
    id: string;
    start: number;
    end: number;
    speaker: string;
    text: string;
    confidence: number;
    duration: number;
  }>;
  diarization_info: any;
}

export interface AnalysisEvent {
  id: string;
  marker_type: 'ATO' | 'SEM' | 'CLU' | 'MEMA';
  marker_subtype: string;
  start_time: number;
  end_time: number;
  confidence: number;
  evidence: string;
  speaker: string;
}

/**
 * Execute TransRapport CLI command via shell - NO HTTP/NETWORK
 */
export async function runMe(args: string[]): Promise<any> {
  const cmd = new Command('me', args); // Uses shell scope defined in tauri.conf.json
  const output = await cmd.execute();
  
  if (output.code !== 0) {
    throw new Error(`CLI failed: ${output.stderr || output.stdout}`);
  }
  
  // Try to parse JSON, fallback to string
  try {
    return JSON.parse(output.stdout);
  } catch {
    return output.stdout.trim();
  }
}

/**
 * Execute with error handling wrapper
 */
async function executeCommand(args: string[]): Promise<CLIResponse> {
  try {
    const data = await runMe(args);
    return {
      success: true,
      data,
      stdout: typeof data === 'string' ? data : JSON.stringify(data),
      stderr: ''
    };
  } catch (error) {
    return {
      success: false,
      error: `${error}`,
      stdout: '',
      stderr: `${error}`
    };
  }
}
// BUTTON MAPPING FUNCTIONS - All offline shell commands only

// BTN_RECORD_START → me audio start --conv <id> --device <name> --format wav
export const startRecording = (conv: string, device?: string) =>
  executeCommand(['audio', 'start', '--conv', conv, '--device', device || 'default', '--format', 'wav']);

// BTN_RECORD_STOP → me audio stop --conv <id> --out ./sessions/<id>/raw.wav  
export const stopRecording = (conv: string, out?: string) =>
  executeCommand(['audio', 'stop', '--conv', conv, '--out', out || `./sessions/${conv}/raw.wav`]);

// BTN_IMPORT_FILE → me job create --conv <id> --text <file.txt>|--audio <file.wav>
export const importTextFile = (conv: string, file: string, description?: string) => {
  const args = ['job', 'create', '--conv', conv, '--text', file];
  if (description) args.push('--description', description);
  return executeCommand(args);
};

export const importAudioFile = (conv: string, file: string, description?: string) => {
  const args = ['job', 'create', '--conv', conv, '--audio', file];
  if (description) args.push('--description', description);
  return executeCommand(args);
};

// BTN_TRANSCRIBE → me transcribe transcribe --conv <id> --model base --lang de
export const transcribe = (conv: string, model = 'base', lang = 'de') =>
  executeCommand(['transcribe', 'transcribe', '--conv', conv, '--model', model, '--lang', lang, '--output-json']);

// BTN_DIARIZE → me diarize diarize --conv <id> --min-duration 1.5
export const diarize = (conv: string, minDuration = 1.5) =>
  executeCommand(['diarize', 'diarize', '--conv', conv, '--min-duration', minDuration.toString(), '--output-json']);

// BTN_ANALYZE → me run scan --conv <id> --window-sem "ANY 2 IN 3" --window-clu "AT_LEAST 1 IN 5"
export const analyze = (conv: string) =>
  executeCommand(['run', 'scan', '--conv', conv, '--window-sem', 'ANY 2 IN 3', '--window-clu', 'AT_LEAST 1 IN 5']);

// BTN_VIEW_ATO → me view events --conv <id> --level ato --last 200
export const viewATO = (conv: string, limit = 200) =>
  executeCommand(['view', 'events', '--conv', conv, '--level', 'ato', '--last', limit.toString(), '--output-json']);

// BTN_VIEW_SEM → me view events --conv <id> --level sem --last 200  
export const viewSEM = (conv: string, limit = 200) =>
  executeCommand(['view', 'events', '--conv', conv, '--level', 'sem', '--last', limit.toString(), '--output-json']);

// BTN_VIEW_CLU → me view events --conv <id> --level clu --last 200
export const viewCLU = (conv: string, limit = 200) =>
  executeCommand(['view', 'events', '--conv', conv, '--level', 'clu', '--last', limit.toString(), '--output-json']);

// BTN_VIEW_MEMA → me view events --conv <id> --level mema --last 200
export const viewMEMA = (conv: string, limit = 200) =>
  executeCommand(['view', 'events', '--conv', conv, '--level', 'mema', '--last', limit.toString(), '--output-json']);

// BTN_EXPORT_REPORT → me export report --conv <id> --format pdf --out exports/<id>/report.pdf
export const exportReport = (conv: string, format = 'pdf') =>
  executeCommand(['export', 'report', '--conv', conv, '--format', format, '--out', `exports/${conv}/report.pdf`]);

// BTN_EXPORT_DATA → me export events --conv <id> --level all --out exports/<id>/
export const exportData = (conv: string) =>
  executeCommand(['export', 'events', '--conv', conv, '--level', 'all', '--out', `exports/${conv}/`]);

// Utility functions
export const getAudioDevices = () =>
  executeCommand(['audio', 'devices']);

export const getStatus = () =>
  executeCommand(['status']);

export const loadMarkers = () =>
  executeCommand(['markers', 'load']);

export const validateMarkers = (strict = true) => {
  const args = ['markers', 'validate'];
  if (strict) args.push('--strict');
  return executeCommand(args);
};