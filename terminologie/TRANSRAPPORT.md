TransRapport (Ubuntu) — Architektur‑Blueprint & Inkrementplan (LD‑3.4)
0. Zielbild

TransRapport ist eine lokale, offlinefähige Marker‑Engine‑Anwendung, die die Pipeline ATO → SEM → CLU → MEMA 1:1 gemäß Spezifikation ausführt. Keine Mocks in der Runtime‑Kette. Ergebnisse werden in lokalen Collections persistiert und sind sofort test- und exportierbar. Die normative Vier‑Ebenen‑Architektur und Regeln stammen aus LEAN.DEEP 3.4 und den beigefügten Beispiel‑/Template‑Dateien.

1. Architekturübersicht
1.1 Ebenen und Rollen

ATO (Atomic Marker): Regex‑basierte Signale auf Token/Surface‑Ebene; definieren pattern und Beispiele.

SEM (Semantic Marker): kombiniert ≥2 distinkte ATO in Fenstern (z. B. „ANY 2 IN 3 messages“). Regel: SEM braucht mindestens zwei unterschiedliche ATO in composed_of.

CLU (Cluster Marker): aggregiert thematisch verwandte SEM über X‑of‑Y‑Fenster; optional mit Scoring/Decay.

MEMA (Meta‑Marker): übergreifende Muster aus mehreren CLUs; Aktivierung als Regelaggregation oder via detect_class.

Die Intuitions‑Marker (familienbasierte CLU_INTUITION_*) sind LD‑3.4‑konform, ohne Schemaänderung, und können nach Sprint 1 in einer contextual_rescan‑Phase ergänzt werden (provisional → confirmed → decayed; Multiplier/EWMA).

1.2 Datenmodell und Collections

Definitionen

markers_atomic, markers_semantic, markers_cluster, markers_meta mit id‑Unique‑Index.
Runtime

events_atomic, events_semantic, events_cluster, events_meta mit {conv: 1, ts: -1} für zeitliche Abfragen pro Konversation.
Ein JS‑Loader lädt YAML aus /markers/* (atomic/semantic/cluster/meta). Diese Struktur ist die Referenz auch für den Offline‑Betrieb.

1.3 Scoring‑Fenster

Für Score‑Fenster und Aggregation (z. B. window.messages, aggregation.method: sum, aggregation.decay) dient das SCR_TEMPLATE als Vorlage.

2. Ubuntu‑Umgebungen (Dev/Test/Prod)

Gleicher Binär‑/CLI‑Pfad in allen Umgebungen, nur andere Verzeichnisse und Daten. Kein HTTP‑Dev‑Sonderweg.

2.1 System‑Voraussetzungen

Ubuntu 22.04/24.04, python3 + venv, pip

Optional Audio‑Vorverarbeitung: ffmpeg (falls Transkription vorangestellt)

2.2 Verzeichnis‑Layout (monorepo)
transrapport/
  markers/
    atomic/     # ATO_*.yaml (pattern + ≥5 examples)             ← ATO-Referenz :contentReference[oaicite:8]{index=8}
    semantic/   # SEM_*.yaml (≥2 ATO, Fensterregel)              ← SEM-Referenz :contentReference[oaicite:9]{index=9}
    cluster/    # CLU_*.yaml (X-of-Y, optional scoring/decay)    ← CLU-Referenz :contentReference[oaicite:10]{index=10}
    meta/       # MEMA_*.yaml (Rule-Agg/Detector)                 ← MEMA-Template :contentReference[oaicite:11]{index=11}
  schemas/
    SCR_TEMPLATE.json   # Score/Aggregationsfenster (Vorlage)     :contentReference[oaicite:12]{index=12}
  engine/
    loader/ ato/ sem/ clu/ meta/ intuition/ store/ cli/
  runtime/           # JSONL oder DB-Dateien pro Umgebung
  exports/
  docs/
    ARCHITECTURE.md
    LEAN.DEEP_3.4.md  # Referenzdokument                            :contentReference[oaicite:13]{index=13}
  LICENSE.md         # CC BY-NC-SA 4.0                               :contentReference[oaicite:14]{index=14}

2.3 Environments

Dev: kleine Beispiel‑Marker, Sample‑Texte, schnelle Iteration.

Test: definierte Testkorpora, „golden runs“, deterministische Fenster/Seeds.

Prod: identische Binaries wie Test, nur andere Pfade; CI‑Schranken verhindern schemawidrige Marker.

3. Pipeline (Runtime‑Fluss)

Ingest: Textdateien/Transkripte laden; optional Audio→Transkript vorgelagert, Output ist immer Text.

ATO‑Detection: Regex‑Match gemäß ATO‑pattern (z. B. „ja, aber“), erzeugt events_atomic.

SEM‑Composition: Prüft Fensterregeln wie „ANY 2 IN 3 messages“ und erzwingt ≥2 distinkte ATO in composed_of, erzeugt events_semantic.

CLU‑Aggregation: X‑of‑Y, z. B. SUM(weight)>=0.8 WITHIN 24h oder AT_LEAST … IN …, erzeugt events_cluster.

MEMA‑Analyse: Regelaggregation über CLUs (z. B. „ANY 3 IN 30 messages“), erzeugt events_meta.

Scoring/Decay: Fenstereinstellungen/Decay an SCR‑Vorlage anlehnen.

Grundprinzip „Bedeutungsverdichtung“: Bedeutung entsteht bottom‑up aus ATO‑Kombinationen über SEM/CLU bis zum MEMA‑Kontext.

4. Schnittstellen: CLI (offline, lokal)

Keine Localhost‑Serverpflicht. Frontend (separat) ruft CLI mit Parametern auf und erhält JSON.

me markers load → lädt YAML aus markers/* (analog YAML‑Loader‑Skizze).

me markers validate --strict → Regeln: examples ≥ 5, „genau ein Strukturblock“ (ATO: pattern | SEM/CLU/MEMA: composed_of | alternativ detect_class), SEM≥2 ATO.

me job create --conv <id> --text <file.txt> [--chunksize N --overlap M]

me run scan --conv <id> [--window.sem "ANY 2 IN 3 messages"] [--window.clu "AT_LEAST 1 IN 5 messages"]

me view events --conv <id> --level {ato|sem|clu|mema} [--last N]

me export events --conv <id> --level all --out ./exports/<id>/

me runtime clear --conv <id>

Event‑Formate (gekürzt)

// ATO
{ "level":"ato", "conv":"demo", "ts":"ISO8601Z", "idx":12, "marker_id":"ATO_*", "text":"..." }
// SEM
{ "level":"sem", "conv":"demo", "ts":"...", "idx":13, "marker_id":"SEM_*", "atos":["ATO_A","ATO_B"] }
// CLU
{ "level":"clu", "conv":"demo", "ts":"...", "idx":17, "marker_id":"CLU_*" }
// MEMA
{ "level":"mema", "conv":"demo", "ts":"...", "idx":25, "marker_id":"MEMA_*" }

5. CI/Qualität

Blocking‑Checks vor jedem Merge:

YAML‑Lint; Schema‑Validierung: examples ≥ 5, SEM≥2 ATO, exakt ein Strukturblock, Prefix‑Lint (ATO/SEM/CLU/MEMA).

Loader‑Smoke‑Test (lädt alle Marker; Schreibzugriff events_* ok).

Score‑Fenster plausibel nach SCR_TEMPLATE.

6. Frontend‑Spezifikation (Buttons → CLI‑Mapping)

Frontend wird separat entwickelt. Nennung ist verbindlich, damit Hooks eindeutig sind.

Input & Aufnahme

BTN_INPUT_FILE_OPEN → me job create --conv … --text <file>

BTN_INPUT_AUDIO_RECORD_TOGGLE(Stop) → me job create --conv … --text <transcript.txt> (Transkription vorgeschaltet)

Chunking

BTN_INPUT_CHUNK_PREVIEW → Vorschau client‑seitig

BTN_INPUT_CHUNK_APPLY → me job create … --chunksize --overlap

Validierung & Lauf

BTN_VALIDATE_MARKERS → me markers validate --strict

BTN_RUN_PIPELINE → me run scan --conv …

BTN_STOP_PIPELINE → Prozess stoppen (Frontend‑seitig)

Ansicht & Export

BTN_VIEW_LEVEL_ATO|SEM|CLU|MEMA → me view events …

BTN_EXPORT_EVENTS_JSONL → me export events --level all

BTN_EXPORT_TRANSCRIPT → Export des Originaltexts

7. Inkrement‑Plan (jede Stufe test‑ und nutzbar)

Nach jedem Inkrement: DoD erfüllt, Demo‑Script vorhanden, Artefakte exportierbar.

INC‑0 — Repo & CI „rot/grün“

Ziel: Gerüst, Loader, Validator.
DoD: me markers validate --strict grün; Loader lädt alle Marker; Beispiele/Regeln enforced.

INC‑1 — Input & Chunking

Ziel: Job‑Erstellung aus Text; deterministische Fenster für Tests.
DoD: me job create erzeugt Messages/Chunks, reproduzierbar per Parametern.

INC‑2 — ATO‑Engine

Ziel: Regex‑Matching gemäß ATO‑pattern; Events persistiert.
DoD: events_atomic enthält Treffer für z. B. „ja, aber“.

INC‑3 — SEM‑Engine

Ziel: Fensterregel „ANY 2 IN 3 messages“; SEM≥2 ATO strikt.
DoD: SEM‑Events nur bei erfüllter Regel.

INC‑4 — CLU‑Engine + Scoring

Ziel: X‑of‑Y‑Aggregation (z. B. SUM(weight)>=0.8 WITHIN 24h), Score/Decay gemäß SCR‑Vorlage.
DoD: CLU‑Events inkl. Score sichtbar; Fenster/Decay nachvollziehbar.

INC‑5 — MEMA‑Engine

Ziel: Regelaggregation über CLUs (z. B. „ANY 3 IN 30 messages“).
DoD: MEMA‑Events erscheinen nur bei erfülltem Fenster.

INC‑6 — Intuition (optional, nach 1. Release)

Ziel: CLU_INTUITION_* in contextual_rescan; Telemetrie (confirmed/retracted/EWMA).
DoD: Intuitions‑Zustände und Multiplier greifen sichtbar.

INC‑7 — TUI

Ziel: Terminal‑UI (Tabs: ATO/SEM/CLU/MEMA), Live‑Status, Fensterindikatoren.
DoD: Live‑Ansicht pro Ebene, Filter pro conv, Export‑Buttons funktionsfähig.

8. Definition of Done (pro Inkrement)

Keine Mocks in der Pipeline.

me markers validate --strict grün (Schema/Beispiele/Strukturblock/SEM≥2 ATO).

me run scan erzeugt reale Events; Export vorhanden.

Kurzes Demo‑Script (scripts/demo_inc<N>.sh), das denselben Output reproduziert.

Kurzes README‑Update in /docs.

9. Teststrategie

Unit: Rule‑Parser (ANY/AT_LEAST/SUM(weight)…), Fenstergrenzen, Regex‑Matcher.

Golden Runs (Test): deterministische Korpora; erwartete ATO/SEM/CLU/MEMA‑Counts als JSON‑Snapshot.

Schema‑Fakes: absichtlich fehlerhafte Marker (fehlende examples, 1‑ATO‑SEM, doppelter Strukturblock) müssen CI brechen.

10. Betrieb & Release (lokal)

Packaging: Zip/Tar des CLI‑Tools samt markers/, schemas/.

Konfiguration: Pfade relativ zum Projekt; keine Netzwerkpflicht.

Lizenz: CC BY‑NC‑SA 4.0 (Namensnennung, nicht kommerziell, Share‑Alike).

11. Anhänge (normative Beispiele)

ATO Beispiel: Regex „ja, aber“; ≥5 Examples.

SEM Beispiel: „ANY 2 IN 3 messages“, composed_of: [ATO_EXAMPLE_SIGNAL, ATO_EXAMPLE_EMOTION].

CLU Beispiel: SUM(weight)>=0.8 WITHIN 24h, window.messages: 50, scoring.decay: 0.01.

MEMA Template: „ANY 3 IN 30 messages“, formula: logistic.

SCR Template: window.messages: 30, aggregation.method: sum, decay: 0.02.

Bedeutungsverdichtung (ATO→…→MEMA): Bottom‑up‑Prinzip.

12. Kurz‑Setup (Ubuntu, Schritt-für-Schritt)
# 1) Projekt holen
git clone <repo> transrapport && cd transrapport

# 2) Python-Umgebung
python3 -m venv .venv && source .venv/bin/activate
pip install pyyaml regex

# 3) Marker/Schema ablegen
#   - markers/atomic/*.yaml … (siehe ATO/SEM/CLU/MEMA-Referenzen)

# 4) Validierung (CI-lokal)
me markers load
me markers validate --strict

# 5) Testlauf
me job create --conv demo --text samples/demo.txt --chunksize 800 --overlap 80
me run scan --conv demo --window.sem "ANY 2 IN 3 messages" --window.clu "AT_LEAST 1 IN 5 messages"
me view events --conv demo --level sem --last 20
me export events --conv demo --level all --out ./exports/demo/

Ergebnis

Mit diesem Blueprint und Plan lieferst du nach jedem Inkrement ein echtes, überprüfbares Teilprodukt. Die Architektur ist voll LD‑3.4‑konform (Vier Ebenen, SEM≥2 ATO, X‑of‑Y‑Fenster, MEMA‑Aggregation; optional Intuition), die Collections/Loader‑Skizze, Beispiele und Scoring‑Vorlagen sind sauber referenziert. Kein Rudern im Localhost‑Nebel, keine „Ende‑der‑Woche‑Überraschung“. Nur klare Regeln, echte Events und stabile Artefakte.

Wenn du willst, hänge ich im Repo direkt eine ARCHITECTURE.md in exakt dieser Form ein und setze die Starter‑Skripte (me‑Wrapper) dazu – ohne Theater.