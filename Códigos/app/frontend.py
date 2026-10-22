"""Resolve os arquivos versionados produzidos pelo Vite."""
import json
from pathlib import Path


def register_frontend(app):
    @app.context_processor
    def frontend_context():
        def frontend_assets():
            manifest = Path(app.static_folder) / "dist/.vite/manifest.json"
            if not manifest.is_file():
                raise RuntimeError(
                    "Build do frontend ausente. Execute npm ci e npm run build em Códigos/frontend."
                )
            return json.loads(manifest.read_text(encoding="utf-8"))["src/main.js"]

        return {"frontend_assets": frontend_assets}
