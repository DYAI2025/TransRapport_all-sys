# TransRapport v0.1.0-pilot

## Highlights
- Offline engine A01–A12 (ATO→SEM→CLU→MEMA), Rapport, exports
- Offline Desktop UI (bundled assets, no HTTP, shell-only IPC)
- SQLCipher storage, CSP connect-src 'none'
- Golden tests green; reproducible outputs

## Known limits
- ASR quality varies by device/model
- Diarization stable for 2–3 speakers

## Quickstart (airplane mode)
me markers validate --strict
me job create --conv demo --text samples/demo.txt --chunksize 800 --overlap 80
me run scan --conv demo
me view events --conv demo --level mema --last 50
me export report --conv demo --format pdf --out exports/demo/report.pdf