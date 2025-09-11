# TransRapport · v0.1.0-pilot

**Offline Transcriber mit LD-3.4 Marker-Analyse (ATO → SEM → CLU → MEMA)**  
Zielgruppe: Therapeut:innen, Rechtsanwält:innen und Berufe mit höchsten Datenschutzanforderungen.  
Kein HTTP, keine Cloud, keine Telemetrie. Alles lokal, nachvollziehbar, reproduzierbar.

## Warum

Cloud-Lösungen sind komplex, teuer und für sensible Daten oft ungeeignet. TransRapport liefert eine verlässliche, vollständig **offline** arbeitende Anwendung, die Gespräche lokal transkribiert, Sprecher trennt, Marker-Ereignisse erkennt und daraus **Rapport-Indikatoren** ableitet. Nutzer zahlen für **Verlässlichkeit, Privatsphäre und Klarheit**.

## Kernfunktionen

- 🎙️ **Aufnahme & Import**: Lokale Audioaufnahme oder Import von WAV/TXT
- ✍️ **Transkription (offline)**: Whisper-Adapter, reproduzierbar
- 🗣️ **Diarisierung (offline)**: Sprechertrennung, manuell korrigierbar
- 🧠 **LD-3.4 Analyse**: ATO → SEM → CLU → MEMA, markerbasiert und auditierbar
- 📈 **Rapport-Verlauf**: Zeitliche Entwicklung mit erklärten Treibern
- 📤 **Exporte**: PDF/JSON/CSV, keine Daten verlassen das Gerät
- 🖥️ **Desktop-UI (offline)**: Gebundelte Assets, **keine** localhost-Server, Shell-IPC zum CLI

## Nicht-Ziele

- Keine Cloud, kein SaaS, kein HTTP/localhost
- Kein Diagnosewerkzeug: Ergebnisse sind Evidenz-gestützt, Entscheidung bleibt beim Menschen

## Systemanforderungen

- Linux, Python 3.11+, Node 18+ (nur Build der UI), ≥4 GB RAM

## Quickstart (Airplane-Mode)

```bash
# Offline-Beweis: Netzwerk aus
nmcli networking off || true

# Marker validieren
me markers validate --strict

# Text-Demo
me job create --conv demo --text samples/demo.txt --chunksize 800 --overlap 80
me run scan --conv demo
me view events --conv demo --level sem --last 50
me export report --conv demo --format pdf --out exports/demo/report.pdf
```

