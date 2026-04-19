import logging
import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class JQuantsAPIClient:
    """Client for J-Quants V2 API."""
    BASE_URL = "https://api.jquants.com/v2"

    def __init__(self) -> None:
        # Support both names for the API key in .env
        self.api_key = os.environ.get("JQUANTS_API_KEY") or os.environ.get("JQUANTS_REFRESH_TOKEN")
        if not self.api_key:
            logger.warning("JQUANTS_API_KEY environment variable is missing.")
        
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_daily_quotes(self, code: str, from_date: str = "", to_date: str = "") -> list[dict[str, Any]]:
        """Fetch daily quotes, normalizing code to 5 digits and applying Free Plan date defaults."""
        if not self.api_key:
            msg = "Missing J-Quants API Key. Please update your .env file."
            raise Exception(msg)

        # Normalize ticker code: append '0' if it's a 4-digit code
        if len(code) == 4 and code.isdigit():
            normalized_code = code + "0"
            logger.info(f"Normalizing ticker {code} to {normalized_code} for V2 API")
        else:
            normalized_code = code

        # Set default dates for Free Plan (12-week delay window)
        from datetime import datetime, timedelta
        now = datetime.now()
        
        # Default 'to' is 14 weeks ago to be very safe (Free plan is 12 weeks delayed)
        if not to_date:
            to_date = (now - timedelta(weeks=14)).strftime("%Y-%m-%d")
        
        # Default 'from' is 700 days before 'to' (Free plan is about 2 years)
        if not from_date:
            target_to = datetime.strptime(to_date, "%Y-%m-%d")
            from_date = (target_to - timedelta(days=700)).strftime("%Y-%m-%d")

        url = f"{self.BASE_URL}/equities/bars/daily"
        headers = {"x-api-key": self.api_key}
        params: dict[str, str] = {
            "code": normalized_code,
            "from": from_date,
            "to": to_date
        }

        all_quotes: list[dict[str, Any]] = []

        while True:
            logger.debug(f"Requesting data for {normalized_code} from {from_date} to {to_date}...")
            response = await self.client.get(url, headers=headers, params=params)

            if response.status_code == 429:
                logger.warning("Rate limit exceeded. Waiting 1s...")
                await asyncio.sleep(1)
                continue

            if response.status_code == 401:
                 msg = "Authentication Error (401): Invalid API Key."
                 raise Exception(msg)
            if response.status_code == 403:
                 msg = f"Permission Error (403): {response.text}"
                 raise Exception(msg)
            if response.status_code >= 500:
                 msg = f"Server Error ({response.status_code})"
                 raise Exception(msg)

            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                response.raise_for_status()
            
            data = response.json()
            # V2 uses "data" field instead of "daily_quotes"
            quotes = data.get("data", [])
            
            # Map V2 shortened field names to the names expected by ETL
            # O -> Open, H -> High, L -> Low, C -> Close, Vo -> Volume
            field_map = {
                "O": "Open",
                "H": "High",
                "L": "Low",
                "C": "Close",
                "Vo": "Volume",
                "Code": "Code",
                "Date": "Date"
            }
            
            mapped_quotes = []
            for q in quotes:
                mapped_q = {}
                for v2_key, full_key in field_map.items():
                    if v2_key in q:
                        mapped_q[full_key] = q[v2_key]
                # Keep other fields as is
                for k, v in q.items():
                    if k not in field_map:
                        mapped_q[k] = v
                mapped_quotes.append(mapped_q)
                
            all_quotes.extend(mapped_quotes)

            pagination_key = data.get("pagination_key")
            if not pagination_key:
                break

            params["pagination_key"] = pagination_key

        return all_quotes

    async def close(self) -> None:
        await self.client.aclose()
