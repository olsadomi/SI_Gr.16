from __future__ import annotations

import argparse

from .config import require_local_target, setting
from .http_client import login


def main() -> int:
    parser = argparse.ArgumentParser(description="Print a crAPI token for local automation")
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    args = parser.parse_args()
    base_url = setting("CRAPI_BASE_URL", "http://localhost:8888")
    require_local_target(base_url)
    print(login(base_url, args.email or setting("CRAPI_ATTACKER_EMAIL"), args.password or setting("CRAPI_ATTACKER_PASSWORD")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

