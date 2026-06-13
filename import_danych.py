import sqlite3
import requests


#Import kategorii
def import_categories():
    response = requests.get(
        API_URL_CATEGORIES,
        timeout=TIMEOUT_SECONDS
    )
    response.raise_for_status()

    categories = response.json()["categories"]

    with engine.begin() as conn:

        for category in categories:

            conn.execute(
                text("""
                    INSERT INTO category (
                        abbreviation,
                        title,
                        description
                    )
                    VALUES (
                        :abbr,
                        :title,
                        :desc
                    )
                    ON CONFLICT DO NOTHING
                """),
                {
                    "abbr": category.get("id"),
                    "title": category["title"],
                    "desc": category.get("description")
                }
            )

    print(f"[INFO] Zaimportowano {len(categories)} kategorii")



#Import zrodel
def import_sources():
    response = requests.get(
        API_URL_SOURCES,
        timeout=TIMEOUT_SECONDS
    )
    response.raise_for_status()

    sources = response.json()["sources"]

    with engine.begin() as conn:

        for source in sources:

            conn.execute(
                text("""
                    INSERT INTO source (
                        title,
                        description
                    )
                    VALUES (
                        :title,
                        :desc
                    )
                    ON CONFLICT DO NOTHING
                """),
                {
                    "title": source["title"],
                    "desc": source.get("url")
                }
            )

    print(f"[INFO] Zaimportowano {len(sources)} źródeł")





if __name__ == "__main__":
    pass