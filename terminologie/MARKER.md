# Marker-Terminologie · Quickref (LD-3.4)

Ziel: Eine knappe Referenz für Entwickler:innen und Reviewer, ohne das LD-3.4-Dok zu wälzen. Für Details stets auf LD-3.4 verweisen.

## 1. Ebenen (Bottom-up)
- **ATO_ (Atomic Marker)** · kleinste beobachtbare Einheit, meist Regex/Token.  
  Struktur: `pattern` + `examples (≥5)`  
  Beispiel: ATO_EXAMPLE_SIGNAL (“ja, aber”).  
- **SEM_ (Semantic Marker)** · Kombination **≥2 distinkter ATO** in einem Fenster (z. B. „ANY 2 IN 3 messages“).  
  Struktur: `composed_of: [ATO_…]` + Fensterregel.  
- **CLU_ (Cluster Marker)** · Aggregation thematisch verwandter SEM_ über X-of-Y-Fenster; optional Scoring/Decay.  
  Struktur: `composed_of: [SEM_…]`, `activation.rule`, optional `scoring`.  
- **MEMA_ (Meta Marker)** · Muster über mehrere CLUs; Regel-Aggregation **oder** `detect_class`.  
  Struktur: `composed_of: [CLU_…]` **oder** `detect_class`, + `activation`/`scoring`.

## 2. Dateien, Loader & Collections
- Marker liegen in: `markers/atomic|semantic|cluster|meta/` (YAML).  
- Loader zieht YAML pro Ordner; Definitionen und Runtime-Events sind getrennt.  
- Collections (Empfehlung):  
  - Definition: `markers_atomic|semantic|cluster|meta` (Unique-Index auf `id`)  
  - Runtime: `events_atomic|semantic|cluster|meta` (Index `{conv, ts}`)

## 3. Minimal-Schema je Marker
**Pflichtfelder (alle Klassen):**
- `id`, `frame{signal, concept, pragmatics, narrative}`, `examples (≥5)`, `tags`
- **genau ein** Strukturblock:  
  - ATO: `pattern`  
  - SEM/CLU/MEMA: `composed_of` **oder** `detect_class`
**Spezifisch:**
- SEM: `composed_of` enthält **≥2** distinkte ATO_  
- CLU: `activation.rule` (X-of-Y), optional `scoring{base, weight, decay, formula}`  
- MEMA: `activation.rule` **oder** `detect_class`; `window` optional für Scores

## 4. Aktivierungs-Cheatsheet (natürliche Regeln)
- `ANY k IN n messages` · mind. *k* Treffer im Fenster von *n* Nachrichten  
- `AT_LEAST x DISTINCT SEMs IN y messages` · mind. *x* verschiedene SEMs im Fenster  
- `SUM(weight) >= t WITHIN 24h` · gewichtete Summe über Zeitraum  
- `window.messages: N` · Rolling Window in Nachrichten

## 5. Scoring & Fenster (Defaults)
- Schablonen liegen in `schemas/` (Score-Window, Aggregation, Decay).  
- Beispiel-Defaults: `window.messages: 30`, `aggregation: sum`, `decay: 0.02`.

## 6. Qualitätsregeln (CI-Blocking)
- `examples ≥ 5` pro Marker
- Präfix-Lint: `ATO_/SEM_/CLU_/MEMA_`
- **Genau ein** Strukturblock (pattern XOR composed_of/detect_class)
- SEM-Komposition: **≥2** ATO_ (1-ATO nur mit begründeter Ausnahme)

## 7. Benennungs-Konventionen
- `ID`: UPPER_SNAKE, präfixiert (`ATO_…`, `SEM_…`, `CLU_…`, `MEMA_…`)
- `tags`: lowercase, thematisch gruppiert
- Dateiname = `id.yaml`

## 8. Leitidee (Bedeutungsverdichtung)
Bedeutung entsteht **bottom-up**: ATO → SEM → CLU → MEMA. ATOs sind neutrale Bausteine; erst Kombinationen erzeugen Bedeutung. Kein psychologisches Raten in ATOs, nur beobachtete Form. SEM/CLU/MEMA heben Bedeutung über Fenster.

## 9. Lizenz
Dokumentation und Templates stehen unter CC BY-NC-SA 4.0.
