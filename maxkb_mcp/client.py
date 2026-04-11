"""HTTP client for MaxKB Admin API with automatic token management."""

from __future__ import annotations

import atexit
import asyncio
import httpx
import time
from typing import Any


class MaxKBClient:
    """Authenticated HTTP client for the MaxKB Admin API."""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.admin_url = f"{self.base_url}/admin/api"
        self.username = username
        self.password = password
        self._token: str | None = None
        self._token_expires: float = 0
        self._http = httpx.AsyncClient(timeout=60, verify=True)

        # Register shutdown hook to close the HTTP client
        atexit.register(self._sync_close)

    def _sync_close(self) -> None:
        """Synchronously close the HTTP client (for atexit)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._http.aclose())
            else:
                loop.run_until_complete(self._http.aclose())
        except Exception:
            pass

    async def __aenter__(self) -> "MaxKBClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def _login(self) -> str:
        resp = await self._http.post(
            f"{self.admin_url}/user/login",
            json={"username": self.username, "password": self.password},
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 200:
            raise RuntimeError(f"MaxKB login failed: {data.get('message')}")
        self._token = data["data"]["token"]
        self._token_expires = time.time() + 3500  # refresh before 1h expiry
        return self._token

    async def _ensure_token(self) -> str:
        if not self._token or time.time() >= self._token_expires:
            return await self._login()
        return self._token

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict | None = None,
        data: Any = None,
    ) -> dict:
        """Make an authenticated request to the MaxKB Admin API."""
        token = await self._ensure_token()
        url = f"{self.admin_url}/{path.lstrip('/')}"
        resp = await self._http.request(
            method,
            url,
            json=json,
            params=params,
            content=data,
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        return resp.json()

    async def get(self, path: str, **kwargs) -> dict:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> dict:
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs) -> dict:
        return await self.request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs) -> dict:
        return await self.request("DELETE", path, **kwargs)

    async def close(self):
        await self._http.aclose()
