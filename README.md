# ClimSmart-Rice
Polygon → Open-Meteo → `.met` → `.apsimx` → APSIM Next Gen (GitHub Actions) → Dashboard + N-timing advisory

| Stage | File |
|---|---|
| Polygon | `assets/polygon.geojson` |
| Settings | `config/config.json` |
| Weather → .met | `pipeline/fetch_weather.py` |
| .apsimx | `pipeline/build_apsimx.py` |
| Run | `.github/workflows/pipeline.yml` |
| Results / Advisory | `pipeline/export_results.py`, `advisory.py` |
| Desktop-style UI | `docs/index.html` (GitHub Pages → `/docs`) |

Edit polygon or config, commit → Actions runs → UI updates.
