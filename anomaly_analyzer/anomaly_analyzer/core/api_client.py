import logging
import os
from datetime import datetime, timedelta
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class JQuantsAPIClient:
    """Client for J-Quants API."""
    BASE_URL = "https://api.jquants.com/v1"

    def __init__(self) -> None:
        self.refresh_token = os.environ.get("JQUANTS_REFRESH_TOKEN")
        self.mail_address = os.environ.get("MAIL_ADDRESS")
        self.password = os.environ.get("PASSWORD")
        if not self.refresh_token and (not self.mail_address or not self.password):
            logger.warning("JQUANTS_REFRESH_TOKEN or MAIL_ADDRESS/PASSWORD environment variables are missing.")
        self.id_token: str | None = None
        self.id_token_expiry: datetime | None = None
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _get_refresh_token(self) -> str:
        """Get refresh token using credentials."""
        url = f"{self.BASE_URL}/token/auth_user"
        data = {
            "mailaddress": self.mail_address,
            "password": self.password
        }
        response = await self.client.post(url, json=data)

        if response.status_code == 401:
            msg = "Authentication failed: Invalid credentials."
            raise Exception(msg)
        response.raise_for_status()

        token_data = response.json()
        return str(token_data["refreshToken"])

    async def _get_id_token(self) -> str:
        """Get ID token using refresh token."""
        if not self.refresh_token:
            self.refresh_token = await self._get_refresh_token()

        url = f"{self.BASE_URL}/token/auth_refresh"
        # Free plan parameter
        params = {"refresh_token": self.refresh_token}
        response = await self.client.post(url, params=params)

        if response.status_code == 401:
             # Refresh token might be expired, try getting a new one
             self.refresh_token = await self._get_refresh_token()
             params = {"refresh_token": self.refresh_token}
             response = await self.client.post(url, params=params)

        response.raise_for_status()
        token_data = response.json()

        self.id_token_expiry = datetime.now() + timedelta(hours=23) # Refresh slightly before 24h
        return str(token_data["idToken"])

    async def _ensure_auth(self) -> str:
        """Ensure we have a valid ID token."""
        if not self.id_token or not self.id_token_expiry or datetime.now() >= self.id_token_expiry:
            self.id_token = await self._get_id_token()
        return self.id_token

    async def fetch_daily_quotes(self, code: str) -> list[dict[str, Any]]:
        """Fetch daily quotes for a specific stock code using pagination."""
        id_token = await self._ensure_auth()
        url = f"{self.BASE_URL}/quotes/daily_quotes"

        headers = {"Authorization": f"Bearer {id_token}"}
        params: dict[str, str] = {"code": code}

        all_quotes: list[dict[str, Any]] = []

        while True:
            response = await self.client.get(url, headers=headers, params=params)

            if response.status_code == 401:
                 msg = "Authentication Error (401)"
                 raise Exception(msg)
            if response.status_code == 403:
                 msg = "Permission Error (403): You may have exceeded your plan limits."
                 raise Exception(msg)
            if response.status_code == 429:
                 msg = "Rate Limit Exceeded (429): Too many requests."
                 raise Exception(msg)
            if response.status_code >= 500:
                 msg = f"Server Error ({response.status_code})"
                 raise Exception(msg)

            response.raise_for_status()
            data = response.json()

            if "daily_quotes" in data:
                 all_quotes.extend(data["daily_quotes"])

            pagination_key = data.get("pagination_key")
            if not pagination_key:
                break

            params["pagination_key"] = pagination_key

        return all_quotes

    async def close(self) -> None:
        await self.client.aclose()
