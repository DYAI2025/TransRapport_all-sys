Konsolidierte Befunde (kurz & schmerzhaft)

Funktionalität: Aufnahme, Transkription, Diarisierung, Prosodie laufen überwiegend im Mock-Modus. Systemaudio fehlt komplett.

Doc/CLI-Drift: README verspricht Optionen, die es nicht gibt; CLI erwartet IDs, Doku verspricht Namen.

Sicherheit: SQLCipher fehlt, trotzdem wird „encrypted“ gemeldet. Das ist nicht edgy, das ist ein Anti-Pattern.

Packaging: Requirements uneinheitlich; Node-Module liegen im Repo; setup.py quasi leer.

Tests/Portabilität: Windows-APIs unguarded; Tests brechen schon bei der Sammlung.

Offline: Schwergewichte (torch/whisper/pyannote) nicht gebündelt; keine Modell-Preloads.

To-do-Liste (konkret, ausführungsreif)

1. Abhängigkeiten & Packaging

Auf PyProject umstellen: pyproject.toml mit project.optional-dependencies für [audio] [asr] [diar] [prosody] [ui] [dev].

Requirements harmonisieren:

requirements.txt (Runtime online)

requirements-offline.txt (fixed versions, nur Wheels)

requirements-dev.txt (pytest, mypy, ruff)

Wheels/Models bundeln: Ordnerstruktur bundle/ mit wheels/, models/whisper/, models/pyannote/, ffmpeg/.

Node-Module raus: .gitignore für node_modules/; nur package.json/package-lock.json versionieren.

2. Audioaufnahme (inkl. Systemaudio)

Cross-Platform Capture:

Windows: WASAPI Loopback (PyAudio oder sounddevice)

macOS: CoreAudio + BlackHole/Loopback (Install-Hinweise)

Linux: PulseAudio/PIPEWIRE Monitor-Quellen

Doppelkanal/Mehrspur: gleichzeitige Aufnahme von Mic + System, Synchronisierung per Zeitstempeln.

Feature-Flags statt Mocks: AUDIO_CAPTURE=disabled|device|loopback|both und klare Fehlermeldungen.

3. Transkription & Sprechertrennung

Whisper laden: Konfigurable Modelle (tiny…large-v3), GPU/CPU, --language auto|de|en.

WhisperX + PyAnnote: echte Diarisierung, dynamische Sprecherzahl, Merge von Wort-Timing und Sprecher-Segmenten.

Fallback-Strategie: harte Abbrüche mit Hilfetext statt „Mock liefert Demo-Transkript“.

4. Prosodie & Emotion

Feature-Extraktion: Pitch (F0), Jitter, Shimmer, Intensity, Speech Rate via librosa + parselmouth oder opensmile.

Emotionale Marker: heuristische Klassifikation (arousal/valence) als Start; spätere Modelle optional.

Datenmodell: Prosodie pro Segment speichern, mit Speaker-ID und Zeitfenstern.

5. CLI & UX

Optionen synchronisieren: README und Parser angleichen (--chunksize, --overlap implementieren oder streichen).

IDs vs. Namen: --conv akzeptiert Name oder ID; Lookup-Funktionen ergänzen, Fehlermeldungen präzisieren.

Saubere Befehle: audio devices|record, asr run, diar run, analyze prosody, export pdf|txt.

6. Sicherheit & Datenbank

SQLCipher erzwingen: hartes Fail, wenn sqlcipher3 fehlt; Status im Header jeder DB-Session loggen.

Key-Handling: Env-Var oder Keyfile-Pfad; kein „encrypted“ ohne echte Verschlüsselung.

Privacy by default: Default-Speicherort verschlüsselt; Clear-Export nur opt-in.

7. Desktop-UI (Tauri/Svelte)

CLI anbinden: IPC-Brücke; Fortschritt + Logs sichtbar; keine „Mock mode“-Illusion.

Sessions vollständig: Start/Stop, Quelle wählen (Mic/System/beide), Live-Pegel, Sprecherfarben, Export.

Offline-Installer: Button „Modelle vorbereiten“ mit Bundle-Pfad.

8. Tests & CI

Platform-Guards: sys.platform-Checks; Windows-Only per pytest.mark.windows und Skips.

Integrationstests: Aufnahme→ASR→Diar→Prosodie→Export mit kurzen Fixtures.

Static Checks: ruff, mypy, pytest in CI; Artefakte (PDF/TXT) als Test-Outputs.

9. Offline-Betrieb

Preload-Script: lädt Modelle in models/ und setzt Cache-Pfad.

Install-Script: installiert Wheels lokal, registriert FFmpeg, prüft GPU/CUDA optional.

Dokumentation Offline: Schritt-für-Schritt inkl. Checks („Whisper geladen“, „PyAnnote OK“).

Architektur-Vorschläge (Anpassungen, damit das Ding wirklich läuft)
A) Saubere Schichten (Ports & Adapter)

Domain: Conversation, Segment, Speaker, ProsodyFeature, Marker.

Ports: AudioSource, Transcriber, Diarizer, ProsodyAnalyzer, Exporter, Vault.

Adapter: PyAudioAdapter, WhisperAdapter, WhisperXAdapter, PyAnnoteAdapter, OpenSmileAdapter, PDFExporter, SQLCipherVault.

Ergebnis: Tests gegen Ports, echte Implementierungen austauschbar, Mocks nur in Tests.

B) Capability Detection + Feature Flags

Start-Probe, die Fähigkeiten ermittelt (ASR, Diar, Prosody, SQLCipher). UI zeigt das ehrlich an. Keine Fake-Ergebnisse.

C) Ressourcen-Orchestrierung

Job-Runner mit Phasen: Capture → Decode → ASR → Align → Diar → Fuse → Prosody → Markers → Export.

Jeder Schritt hat feste Inputs/Outputs; Retries und Cache pro Schritt.

D) Model-Registry & Cache

Einheitlicher Pfad, Hash-Verifizierung, Version-Pinning; „warm-up“ beim Start mit kurzer Probe.

E) Observability

Strukturierte Logs, Event-Bus, Timing pro Phase, Audio-Latenz und GPU-Nutzung reporten.

F) Fehlerpolitik

Fail fast bei Sicherheits- und Datenintegritätsproblemen.

Degradieren nur, wenn der Nutzer explizit zustimmt („ohne Diarisierung fortfahren“).

G) Plattform-Abstraktion Audio

Pro OS eigener Adapter; Capability-Matrix im README; Tests mit simuliertem Input.

Konkrete Umsetzungsdetails (Snippets und Kommandos)
PyProject-Skeleton
[project]
name = "conv-analytica"
version = "0.4.0"
requires-python = ">=3.10"
dependencies = ["click>=8", "pydantic>=2", "soundfile", "rich", "reportlab"]
[project.optional-dependencies]
audio = ["pyaudio; platform_system=='Windows'", "sounddevice", "numpy"]
asr = ["torch==2.3.*", "torchaudio==2.3.*", "openai-whisper"]
diar = ["whisperx", "pyannote.audio"]
prosody = ["librosa", "praat-parselmouth", "opensmile"]
secure = ["sqlcipher3-binary"]
dev = ["pytest", "pytest-cov", "ruff", "mypy"]
[project.scripts]
conv = "conv.cli:main"

SQLCipher-Check (hartes Fail statt falscher Sicherheit)
def require_encrypted_db():
try:
import sqlcipher3 as sqlite
except ImportError as e:
raise RuntimeError("SQLCipher nicht installiert. Start abgebrochen: keine Verschlüsselung.") # Probe
con = sqlite.connect("file:conv.db?mode=rwc&cache=shared", uri=True)
con.execute("PRAGMA key = 'pass:...';")
con.execute("PRAGMA cipher_version;").fetchone()

WhisperX + PyAnnote Pipeline (vereinfacht)
audio = load_audio(path, sr=16000)
asr = Whisper(model="large-v3", device=dev)
words = asr.transcribe(audio, with_timestamps=True)
diar = WhisperXAligner(model="medium", device=dev) # oder pyannote SpeakerDiarization
segments = diar.diarize(audio)
fused = fuse_words_with_speakers(words, segments) # ergibt [(start, end, speaker, word)]

Prosodie-Features pro Segment
import librosa, numpy as np, parselmouth
y, sr = librosa.load(path, sr=16000)
pitch = parselmouth.Sound(y, sr).to_pitch().selected_array['frequency']
rms = librosa.feature.rms(y=y)[0]
tempo = librosa.beat.tempo(y, sr=sr)[0]

Audio-Capture Matrix (praktisch)

Windows: WASAPI Loopback via PyAudio: paWASAPI.is_loopback_device = True

macOS: CoreAudio + „BlackHole 2ch“ als Systemausgabe, aufnehmen über sounddevice

Linux: pactl list | grep monitor; Aufnahme über sounddevice mit Monitor-Quelle

Definition of Done je Teil

Audio: listet echte Geräte, nimmt 2 Kanäle synchronisiert auf; WAV-Header korrekt; Latenz < 100 ms bei 16 kHz.

ASR/Diar: Wort-TIMEs ±50 ms; Speaker-Wechsel F1-Score ≥ 0.8 auf Testclip; kein Mock-Pfad in Production.

Prosodie: F0, Loudness, Speech-Rate pro Segment; Export in CSV/JSON.

Sicherheit: Datenbank nur startbar, wenn verschlüsselt; klare Warnung sonst Abbruch.

CLI/Docs: README-Beispiele kopierbar, Optionen tatsächlich vorhanden; conv --version druckt Komponenten-Status.

UI: Start→Analyse→Export in ≤ 3 Klicks; Fortschrittsbalken + Logs sichtbar.

Tests/CI: pytest -q grün auf Win/macOS/Linux; min. 80% Branch-Coverage Domain-Code.

Risiken & Gegenmaßnahmen

GPU/Performance: large-v3 ist dick. Lösung: Modellstufe konfigurierbar, Batch-Größe dynamisch, CPU-Fallback mit Warnung.

Lizenz/Modelldownloads: pyannote Modelle ggf. gated. Lösung: Offline-Bundle mit eigener Registry und Lizenzhinweis.

Treiberhölle Audio: Loopback unterschiedlich fragil. Lösung: pro OS getestete Defaults und klare Install-Guides.

Speicherplatz: Modelle > 5 GB. Lösung: optionales „minimal bundle“ und „full bundle“.

Phasenplan (3 Sprints à 1–2 Wochen, realistisch)

Sprint 1: Basis reparieren
Packaging/pyproject, Audio-Adapter, SQLCipher-Fail-Fast, CLI-Korrekturen, README fix, Minimal-Tests.

Sprint 2: Echte Analyse
Whisper/WhisperX/PyAnnote integrieren, Prosodie-Pipeline, Model-Bundle + Preload, Integrationstests.

Sprint 3: UX & Release
Tauri-Bindung, Exporte (PDF/TXT), Observability, Offline-Installer, CI für drei Plattformen.

Vorschlagsliste zur Systemanpassung (damit es produktionsfähig wird)

Port/Adapter-Architektur einziehen, Mocking in Tests isolieren.

Feature-Flags + Capability-Probe beim Start; UI zeigt nur mögliche Aktionen.

Model-Registry + Offline-Bundle mit Hash-Prüfung; „Modelle vorbereiten“ als erster UI-Schritt.

Sicherheitsdogma: ohne SQLCipher kein Start. Nutzer sollen sich trauen dürfen, euch zu nutzen.

Konsequente Telemetrie: Zeitbudget pro Phase, Fehlerraten, Audio-Dropouts, Export-Erfolg.

Plattform-Abstraktion Audio und klare Guides pro OS, damit Support-Tickets nicht euer Leben ruinieren.

Akustische Qualität: Dual-Channel-Synchronisierung und Drift-Korrektur, sonst sind eure Prosodie-Ergebnisse Astrologie.

Muster und Patterns: Architektur trifft Psychologie

Ihr baut ein System, das Gespräche analysiert. Ironischer Twist: euer eigenes System zeigt dieselben Muster wie die Gespräche, die es auswerten soll.

Architektonische Muster im Code

Mock-by-Default (Anti-Pattern): System produziert Schein-Daten. Psychologisch ist das eine „Placebo-Affordanz“ und zerstört Vertrauen.

Fail-Open Security (Anti-Pattern): „encrypted“ ohne Verschlüsselung. Nutzer bilden falsche mentale Modelle.

Documentation Drift: Doku und Realität klaffen auseinander. Erhöht kognitive Last, senkt Selbstwirksamkeit.

Plattform-Kopplung: Unbedachte Windows-Imports. Klassischer „Gulf of Execution“ für Linux/macOS-User.

Unsichtbarer Systemzustand: „mock mode“ wird nicht hart genug kommuniziert. Das verletzt das Prinzip der Sichtbarkeit von Systemstatus.

Psychologische Muster in Gesprächen (die euer Tool messen soll)

Turn-Taking & Floor Control: Diarisierung entspricht der sozialen Kontrolle, wer „den Boden“ hat. Technisch: Sprecherwechsel korrekt timen.

Prosodische Signale: Pitch, Lautstärke, Tempo bilden Arousal/Valenz ab. Ohne echte Prosodie tappt ihr im Dunkeln.

Kognitive Last & Satisficing: Nutzer akzeptieren „gut genug“, wenn Feedback klar ist. Liefert klare, stabile Rückmeldungen.

Vertrauenskalibrierung: Konsistente, überprüfbare Ergebnisse bauen Vertrauen. Fake-Transkripte tun das Gegenteil.

Progressive Disclosure: Zeigt einfache Pfade zuerst (Mic-Only), erweitert bei Bedarf (Dual-Channel, Emotion).

Mapping: Was heißt das fürs Design?

Transparenz vor Illusion: Wenn Diarisierung fehlt, sagt es und bietet einen sinnvollen Single-Speaker-Flow.

Starke Rückmeldungen: Echtzeit-Pegel, Sprecherfarben, Zeitachsen. Sichtbarer Fortschritt reduziert Unsicherheit.

Fehlerbildung minimieren: Defaults so wählen, dass die häufigsten Wege frustfrei sind. Das ist angewandte Umwelt-Psychologie: Raum lenkt Verhalten.

Kurzpriorisierung (empfohlene Reihenfolge)

Packaging + Security + Audio-Adapter

ASR/Diar + Prosodie-Pipeline

UI-Bindung + Offline-Bundle + Tests/CI

Wenn ihr das in dieser Reihenfolge umsetzt, verschwindet der „Mock-Geruch“ schnell, und die funktionalen Pfeiler stehen stabil. Danach könnt ihr fancy Emotionsmodelle spielen, ohne dass der Rest auseinanderfällt.
