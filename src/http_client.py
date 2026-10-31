from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: str

    def json(self) -> Any:
        return json.loads(self.body)


def request_json(
    method: str,
    url: str,
    *,
    payload: Any | None = None,
    token: str | None = None,
    timeout: float = 30,
) -> Response:
    headers = {"Accept": "application/json"}
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, data=body, headers=headers, method=method.upper())
    try:
        with urlopen(req, timeout=timeout) as response:
            return Response(response.status, dict(response.headers), response.read().decode("utf-8"))
    except HTTPError as error:
        return Response(error.code, dict(error.headers), error.read().decode("utf-8"))
    except URLError as error:
        raise RuntimeError(f"Cannot reach {url}: {error.reason}") from error


def login(base_url: str, email: str, password: str) -> str:
    response = request_json(
        "POST",
        f"{base_url.rstrip('/')}/identity/api/auth/login",
        payload={"email": email, "password": password},
    )
    if response.status != 200:
        raise RuntimeError(f"Login failed for {email}: HTTP {response.status}: {response.body[:200]}")
    token = response.json().get("token")
    if not token:
        raise RuntimeError(f"Login response for {email} did not contain a token")
    return token

