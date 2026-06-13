from typing import Any
from time import sleep
import requests


TIMEOUT_SECONDS = 30




def fetch_source():
    api_url = "https://eonet.gsfc.nasa.gov/api/v3/sources"

    for attempt in range(1, 4):
        try:
            response = requests.get(
                api_url,
                headers={"Accept": "application/json"},
                timeout=TIMEOUT_SECONDS,
            )

            response.raise_for_status()

            payload = response.json()
            # Pobieramy klucz "sources", a nie "events"
            sources = payload.get("sources", [])

            if not isinstance(sources, list):
                raise ValueError("API zwróciło dane o źródłach w nieoczekiwanym formacie.")

            return sources

        except requests.RequestException as error:
            print(f"Pobieranie źródeł - Próba {attempt}/3 nie powiodła się: {error}")
            if attempt < 3:
                sleep(3)
                
    return None 

def fetch_categories():
    api_url = "https://eonet.gsfc.nasa.gov/api/v3/categories"

    for attempt in range(1, 4):
        try:
            response = requests.get(
                api_url,
                headers={"Accept": "application/json"},
                timeout=TIMEOUT_SECONDS,
            )

            response.raise_for_status()

            payload = response.json()
            categories = payload.get("categories", [])

            if not isinstance(categories, list):
                raise ValueError("API zwróciło dane o kategoriach w nieoczekiwanym formacie.")

            return categories

        except requests.RequestException as error:
            print(f"Pobieranie kategorii - Próba {attempt}/3 nie powiodła się: {error}")
            if attempt < 3:
                sleep(3)
                
    return None

def fetch_events(days, limit ) -> list[dict[str, Any]]:
    api_url = "https://eonet.gsfc.nasa.gov/api/v3/events"
    params = {
        "status": "all",
        "days": days,
        "limit": limit,
    }

    for attempt in range(1, 4):
        try:
            response = requests.get(
                api_url,
                params=params,
                headers={"Accept": "application/json"},
                timeout=TIMEOUT_SECONDS,
            )

            response.raise_for_status()

            payload = response.json()
            events = payload.get("events", [])

            if not isinstance(events, list):
                raise ValueError("API zwróciło dane w nieoczekiwanym formacie.")

            return events

        except requests.RequestException as error:
            print(f"Próba {attempt}/3 nie powiodła się: {error}")

            if attempt < 3:
                sleep(3)

    return []
