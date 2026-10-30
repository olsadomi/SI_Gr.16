from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def load_dotenv(path: Path | None = None) -> dict[str, str]:
    """Load a minimal KEY=VALUE file without overriding the process environment."""
    source = path or ROOT / ".env"
    values: dict[str, str] = {}
    if source.exists():
        for raw in source.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def setting(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, load_dotenv().get(name, default))
    if value is None:
        raise RuntimeError(f"Missing required setting: {name}")
    return value


def require_local_target(url: str) -> None:
    """Prevent accidental active testing of non-local systems."""
    parsed = urlparse(url)
    allowed = {"localhost", "127.0.0.1", "::1", "host.docker.internal"}
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in allowed:
        raise RuntimeError(
            f"Refusing target {url!r}. Only the local Docker lab is authorized."
        )

