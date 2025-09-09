# Feature Specification: TransRapport Offline Desktop Application

**Feature**: TransRapport Offline Desktop Application  
**Date**: 2025-09-08  
**Branch**: `003-transrapport-offline-desktop`

## Problem Statement

**Target Users**: Therapeut:innen, Rechtsanwält:innen, beratende Berufe mit Vertraulichkeitspflichten

**Core Problem**: Cloud-Lösungen sind komplex, teuer, intransparent und für sensible Daten oft unerwünscht.

**Value Proposition**: Ein schlankes Offline-Tool, das „einfach funktioniert", nichts hochlädt, vertrauenswürdig ist und nutzbare Ergebnisse liefert: Transkript, Sprechertrennung, Marker-Ereignisse, Rapport-Indikatoren, Export.

## Product Purpose

TransRapport ist Vertrauen zum Installieren: lokal, nachvollziehbar, schön genug, um täglich benutzt zu werden, und wertvoll, weil es Sinn aus Gesprächen gewinnt, ohne die Privatsphäre zu verraten.

**CRITICAL**: Von diesem Zweck darf nicht abgewichen werden. Nutzer:innen zahlen für Verlässlichkeit, Privatsphäre und Klarheit, nicht für „mehr Features".

## Functional Requirements

### FR-001: Recording & Import
- **FR-001.1**: Live-Aufnahme lokal via Mikrofon und optional Systemsound ohne externe Dienste
- **FR-001.2**: Batch-Import lokaler Audio-Dateien oder vorhandener Transkripte  
- **FR-001.3**: Speicherung von Sitzungs-Metadaten: Fall-/Klientenkürzel, Datum, Kontext, Einwilligungshinweis
- **FR-001.4**: Alle Daten bleiben komplett lokal, kein Netzwerkzugriff

### FR-002: Offline Speech Recognition & Diarization
- **FR-002.1**: ASR lokal mit austauschbarem, adapter-basiertem Modell
- **FR-002.2**: Near-real-time Transkription (Zuverlässigkeit vor Geschwindigkeit)
- **FR-002.3**: Sprecher-Diarisierung offline: Sprecher A/B/C erkennen mit manueller Korrektur
- **FR-002.4**: Korrektur-Modus mit Texteditor, Undo/Redo, Zeitstempel

### FR-003: LD-3.4 Marker Analysis (Offline)
- **FR-003.1**: LD-3.4-Pipeline: ATO → SEM → CLU → MEMA Marker-Analyse
- **FR-003.2**: Input: Transkript + Sprechersegmente
- **FR-003.3**: Output: Marker-Events mit Zeitstempel, Speaker-Bezug, Regelkontext
- **FR-003.4**: Rapport-Indikatoren aus Marker-Mustern: Rapport/Lageskala, Dialog-Dynamiken
- **FR-003.5**: Alle Indikatoren klar begründet und nachvollziehbar (Transparenz-Prinzip)

### FR-004: Review & Analysis Interface
- **FR-004.1**: Zeitachsen-Ansicht: Transkript links, Marker-Ereignisse rechts
- **FR-004.2**: Filter nach Ebene (ATO/SEM/CLU/MEMA) und Sprecher
- **FR-004.3**: Sitzungssummary mit Rapport-Verlauf und auffälligen Sequenzen
- **FR-004.4**: Marker-Begründung einsehbar: warum getriggert, aus welchen Mustern

### FR-005: Local Export & Reporting
- **FR-005.1**: Export lokal: Transkript (.txt/.md), Marker-Events (.jsonl/.csv), Kurzbericht (.pdf/.md)
- **FR-005.2**: Speicherort wählbar (z.B. in Fallordner)
- **FR-005.3**: Keine Cloud-Übergabe, keine Telemetrie
- **FR-005.4**: Vollständige Lösch-Funktion inkl. Index-Einträge

### FR-006: Single-Window UI Design
- **FR-006.1**: Klare Primäraktionen: „Aufnahme starten/stoppen", „Datei importieren", „Analyse starten", „Bericht exportieren"
- **FR-006.2**: Default-Pfad: Aufnahme/Import → Transkript prüfen → Analyse → Marker/Rapport prüfen → Export
- **FR-006.3**: Sprecherlabels und Transkript korrigierbar, Analyse erneut ausführbar
- **FR-006.4**: „Erstaufnahme bis Export" ohne Handbuch machbar

### FR-007: Data Protection & Privacy
- **FR-007.1**: Alles lokal: Audio, Transkripte, Marker-Events, Berichte
- **FR-007.2**: Optionale Verschlüsselung des lokalen Speichers
- **FR-007.3**: Protokollierbarkeit: Lokale Logs ohne personenbezogene Inhalte
- **FR-007.4**: Funktioniert im Flugmodus, blockiert Netzwerkzugriffe

## User Scenarios

### US-001: Therapeutin Remote-Sitzung
**Als** Therapeutin mit Remote-Sitzung via Teams/Zoom  
**möchte ich** die Sitzung lokal aufnehmen, transkribieren und analysieren  
**damit** ich Rapport-Verläufe und Dialog-Dynamiken für meine Dokumentation erhalte

**Acceptance Criteria**:
- Startet TransRapport, Aufnahme starten während Online-Sitzung
- Nach Sitzung Stopp, lokale Transkription automatisch
- Sprecher A/B Zuordnung prüfbar und korrigierbar
- Analyse startet → Marker-Ereignisse und Rapport-Kurve erscheinen
- Markante Stellen reviewbar, Bericht exportierbar und lokal ablegen
- Kein Datenabfluss außerhalb des Geräts

### US-002: Anwalt Mandantengespräch
**Als** Rechtsanwalt mit Mandantengespräch im Büro  
**möchte ich** Audio-Aufzeichnung importieren und analysieren  
**damit** ich Dialog-Verläufe und Gesprächsdynamiken für die Mandantenakte dokumentiere

**Acceptance Criteria**:
- WAV-Mitschnitt vom Rekorder importierbar
- Transkript generieren, Sprecher zuordnen
- Analyse → Marker-Evidenzen, Sequenzen, Zusammenfassung
- Export in Mandantenakte möglich
- Keine Daten verlassen das Gerät, vollständig offline

### US-003: Berater Klientengespräch
**Als** beratender Beruf mit Vertraulichkeitspflichten  
**möchte ich** Gespräche strukturiert analysieren  
**damit** ich Gesprächsverläufe und Rapport-Indikatoren nachvollziehbar dokumentiere

## Non-Functional Requirements

### NFR-001: Privacy First
- Funktioniert im Flugmodus
- Blockiert alle Netzwerkzugriffe  
- Kein Cloud, kein SaaS, keine Server-Abhängigkeit
- Keine Hintergrund-Uploads, keine Telemetrie

### NFR-002: Reliability over Speed
- Reproduzierbare Ergebnisse
- Verständliche Fehlerbilder
- Near-real-time okay, Zuverlässigkeit hat Vorrang
- Wiederholbarkeit: Gleicher Input → gleiche Marker-Ergebnisse

### NFR-003: Transparency
- Jeder Rapport-Indikator auf Marker-Evidenz zurückführbar
- Marker-Definitionen als YAML-Dateien mit Versionierung
- Nachvollziehbare Begründungen für alle Analysen
- Klare Logs für Protokollierbarkeit

### NFR-004: Usability
- „Erstaufnahme bis Export" ohne Handbuch machbar
- Einfacher Pfad: max. 5 klare Schritte
- Single-Window-App mit klaren Primäraktionen
- Korrekturen möglich, Analyse wiederholbar

### NFR-005: Performance
- 60–120-Min-Sitzung auf Standard-Laptop offline analysierbar
- Adapter-basierte ASR-Modelle austauschbar
- Lokale Speicherung optimiert
- Mindestens zwei Sprecher erkenn- und editierbar

### NFR-006: Maintainability  
- Marker-Definitionen als Dateien (YAML) mit Versionierung
- Klare Logs ohne personenbezogene Inhalte
- Adapter-Prinzip: ASR/Modelle austauschbar, bleiben lokal
- LD-3.4-konform: ATO→SEM→CLU→MEMA als feste Semantik-Pipeline

## Explicit Non-Goals

### NG-001: No Cloud Dependencies
- Keine Cloud, kein SaaS, keine Server-Abhängigkeit
- Keine Hintergrund-Uploads oder Telemetrie
- Kein Netzwerkzugriff erforderlich

### NG-002: No Diagnostic Tool
- Kein Diagnosetool und kein Ersatz für fachliche Beurteilung
- Interpretationen bleiben transparent und prüfbar
- Tool unterstützt, ersetzt aber keine fachliche Beurteilung

### NG-003: No Feature Bloat
- Kein „Feature-Feuerwerk" zulasten von Einfachheit
- Stabilität und Verständlichkeit haben Vorrang
- Nutzer zahlen für Verlässlichkeit, nicht für mehr Features

## Acceptance Criteria

### AC-001: Offline Verification
- Anwendung funktioniert vollständig ohne Internet
- Netzwerkzugriffe sind deaktiviert/blockiert
- Funktioniert im Flugmodus-Test

### AC-002: Transparency
- Jede Marker-Aussage zeigt „warum" (Regel, Fundstellen, Fenster)
- Marker-Evidenzen nachvollziehbar und prüfbar
- Rapport-Indikatoren auf Marker-Patterns zurückführbar

### AC-003: Local Export
- Transkript, Marker-Events, Summary lokal speicherbar
- Speicherort wählbar (Fallordner)
- Verschiedene Formate: .txt/.md, .jsonl/.csv, .pdf/.md

### AC-004: Speaker Diarization
- Mindestens zwei Sprecher lokal erkenn- und editierbar
- Manuelle Korrektur der Sprecher-Zuordnung möglich
- Sprecherlabels korrigierbar, Analyse wiederholbar

### AC-005: Reproducibility
- Gleicher Input → gleiche Marker-Ergebnisse
- Reproduzierbare Analysen und Berichte
- Nachvollziehbare Verarbeitungskette

### AC-006: Simple Path
- Aufnahme/Import bis Bericht in maximal 5 klaren Schritten
- Primäraktionen klar erkennbar und verwendbar
- Ohne Handbuch von Erstaufnahme bis Export machbar

## Technical Constraints

### TC-001: No Network Access
- Die Anwendung darf keine externen Dienste ansprechen
- Offline-Betrieb ist Pflicht, nicht Option
- Netzwerk-Blocking implementiert

### TC-002: Adapter Architecture
- ASR/Modelle sind austauschbar, bleiben aber lokal
- Klare Adapter-Interfaces für verschiedene ASR-Engines
- Modell-Updates ohne Cloud-Abhängigkeit

### TC-003: LD-3.4 Compliance
- Marker-Regeln: LD-3.4-konform
- ATO→SEM→CLU→MEMA als feste Semantik-Pipeline
- Marker-Definitionen in versionierten YAML-Dateien

### TC-004: Desktop Platform
- Native Desktop-Anwendung (nicht Web-basiert)
- Standard-Laptop-Performance (60-120 Min Sitzungen)
- Lokale Dateisystem-Integration

## Risk Assessment

### High Risk
- ASR-Qualität bei verschiedenen Audioqualitäten und Dialekten
- Speaker Diarization Genauigkeit bei ähnlichen Stimmen  
- LD-3.4 Marker-Pipeline Implementierung und Validierung

### Medium Risk
- Performance bei längeren Sitzungen (>120 Min)
- Audio-Format Kompatibilität und Import-Robustheit
- UI/UX Balance zwischen Einfachheit und Funktionalität

### Low Risk
- Lokale Datenspeicherung und -sicherheit
- Export-Funktionalität in verschiedenen Formaten
- Offline-Betrieb ohne Netzwerk-Abhängigkeiten

## Success Metrics

### Primary Metrics
- **User Adoption**: Nutzer verwenden Tool regelmäßig für echte Fälle
- **Privacy Compliance**: 100% offline Verifikation, keine Datenlecks
- **Usability**: Nutzer kommen ohne Handbuch von Start bis Export

### Secondary Metrics  
- **Accuracy**: ASR-Genauigkeit >95% bei Standard-Audio
- **Performance**: 60-Min-Sitzung in <10 Min analysiert
- **Reliability**: Reproduzierbare Ergebnisse bei identischem Input

## Dependencies

### Internal Dependencies
- Existing LD-3.4 Marker-Pipeline (CLI implementation)
- TransRapport marker definitions and rules
- Documentation and terminology system

### External Dependencies  
- Local ASR Engine (adapter-based, exchangeable)
- Desktop UI Framework (native, cross-platform)
- Audio processing libraries (local, offline)
- PDF/Document generation libraries (local)

## NEEDS CLARIFICATION

### NEEDS CLARIFICATION 1: Desktop Platform Choice
**Question**: Which desktop platform(s) to target first?
**Options**: 
- Windows (most common in professional environments)
- macOS (common among consultants/therapists) 
- Linux (privacy-focused users)
- Cross-platform from start

### NEEDS CLARIFICATION 2: ASR Engine Selection
**Question**: Which offline ASR engine to use as primary adapter?
**Options**:
- OpenAI Whisper (local)
- Mozilla DeepSpeech
- wav2vec2 models
- German-optimized models for target audience

### NEEDS CLARIFICATION 3: UI Framework
**Question**: Which desktop UI framework for native feel and performance?
**Options**:
- Electron (web-based, familiar dev)
- Qt/PySide (native, cross-platform)
- .NET (Windows-native)
- Tauri (Rust + web frontend)

### NEEDS CLARIFICATION 4: Audio Processing Pipeline
**Question**: How to handle audio input/processing chain?
**Details**: 
- Real-time vs batch processing
- Audio format support priorities
- Buffer management for live recording
- Audio enhancement/preprocessing needs

### NEEDS CLARIFICATION 5: LD-3.4 Pipeline Integration
**Question**: How to integrate existing LD-3.4 marker analysis?
**Options**:
- Direct integration of existing CLI
- Reimplement for desktop app
- Hybrid: CLI for analysis, GUI for interaction

### NEEDS CLARIFICATION 6: Data Storage Architecture
**Question**: Local storage structure and format?
**Details**:
- SQLite vs file-based storage
- Encryption at rest implementation
- Session data organization
- Index structure for searchability

### NEEDS CLARIFICATION 7: Speaker Diarization Approach
**Question**: How to implement speaker diarization offline?
**Options**:
- Integrated with ASR engine
- Separate diarization models
- Hybrid automatic + manual approach
- Voice embedding clustering

### NEEDS CLARIFICATION 8: Export Format Priorities
**Question**: Which export formats are most critical for target users?
**Details**:
- Professional report templates
- Legal documentation standards
- Therapeutic documentation requirements
- Integration with existing tools

---

**Status**: Specification Complete - Pending Clarifications  
**Next Steps**: Address clarifications, then proceed to `/plan` command for implementation planning