import sqlite3
import requests

#Import kategorii
with sqlite3.connect(DB_PATH) as conn:

    response = requests.get(API_URL_CATEGORIES, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()

    categories = response.json()["categories"]

    for category in categories:
        conn.execute(
            """
            INSERT OR IGNORE INTO category
            (api_id, title, description)
            VALUES (?, ?, ?)
            """,
            (
                str(category["id"]),
                category["title"],
                category.get("description")
            )
        )

    conn.commit()

#Import zrodel
with sqlite3.connect(DB_PATH) as conn:

    response = requests.get(API_URL_SOURCES, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()

    sources = response.json()["sources"]

    for source in sources:
        conn.execute(
            """
            INSERT OR IGNORE INTO source
            (abbreviation, title, link)
            VALUES (?, ?, ?)
            """,
            (
                source["id"],
                source["title"],
                source.get("url")
            )
        )

    conn.commit()


#Import wydarzen
response = requests.get(
    f"{API_URL_EVENTS}?limit={EVENT_LIMIT}",
    timeout=TIMEOUT_SECONDS
)

response.raise_for_status()

events = response.json()["events"]

with sqlite3.connect(DB_PATH) as conn:

    saved = 0

    for event in events:

        conn.execute(
            """
            INSERT OR IGNORE INTO event
            (api_id, title, description, start, end, state, county)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["id"],
                event["title"],
                None,
                event.get("geometry", [{}])[0].get("date"),
                None,
                event.get("closed"),
                None
            )
        )

        saved += 1

    conn.commit()


