from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Callable, Optional


class FilingCache:
    """Disk cache for downloaded SEC filing HTML and parsed bundles."""

    def __init__(self, cache_dir: str | Path = ".cache/filings", enabled: bool = True) -> None:
        self.cache_dir = Path(cache_dir)
        self.enabled = enabled
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key_path(self, namespace: str, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        return self.cache_dir / namespace / f"{digest}.json"

    def get_html(self, cache_key: str, fetch_fn: Callable[[], str]) -> str:
        """Return cached HTML or fetch and store."""
        if not self.enabled:
            return fetch_fn()

        path = self._key_path("html", cache_key)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data["html"]

        html = fetch_fn()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"html": html}), encoding="utf-8")
        return html

    def get_bundle(self, cache_key: str, build_fn: Callable[[], dict]) -> dict:
        """Return cached filing bundle (chunks + metadata) or build and store."""
        if not self.enabled:
            return build_fn()

        path = self._key_path("bundle", cache_key)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))

        bundle = build_fn()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(bundle), encoding="utf-8")
        return bundle

    def clear(self, namespace: Optional[str] = None) -> int:
        """Remove cached files. Returns count removed."""
        if not self.cache_dir.exists():
            return 0
        removed = 0
        if namespace:
            target = self.cache_dir / namespace
            if target.exists():
                for f in target.glob("*.json"):
                    f.unlink()
                    removed += 1
        else:
            for f in self.cache_dir.rglob("*.json"):
                f.unlink()
                removed += 1
        return removed
