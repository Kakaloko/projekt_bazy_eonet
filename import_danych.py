import sqlite3
import requests
from sqlalchemy import text
import  reverse_geocode as  rg

#Import kategorii
def import_categories(categories, engine):

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
def import_sources(sources, engine):

    with engine.begin() as conn:

        for source in sources:

            conn.execute(
                text("""
                    INSERT INTO source (
                        title,
                        abbreviation,
                        description
                    )
                    VALUES (
                        :title,
                        :abbreviation,
                        :desc
                    )
                    ON CONFLICT DO NOTHING
                """),
                {
                    "title": source["title"],
                    "abbreviation": source.get("id"),
                    "desc": source.get("url")
                }
            )

    print(f"[INFO] Zaimportowano {len(sources)} źródeł")











def import_event(events , engine) -> None:

    try:
        with engine.begin() as conn:

            for event in events:

                
                if not event.get("id") or not event.get("title") or not event.get("geometry"):
                    continue

                
                event_id = int(str(event["id"]).replace("EONET_", ""))
                title = event["title"].split(",")[0].strip()
                description = event.get("description")

                start_date = event["geometry"][0]["date"]
                end_date = event.get("closed")

                conn.execute(
                    text("""
                        INSERT INTO event (
                            id, title, description, start_date, end_date
                        )
                        VALUES (
                            :id, :title, :description, :start_date, :end_date
                        )
                        ON CONFLICT (id) DO NOTHING
                    """),
                    {
                        "id": event_id,
                        "title": title,
                        "description": description,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                )

                
                last_lat = None
                last_lon = None

                for geom in event["geometry"]:

                    coords = geom.get("coordinates", [None, None])
                    lon = coords[0]
                    lat = coords[1]

                    if lon is not None and lon > 180:
                        lon = lon - 360
                    
                    last_lat = lat
                    last_lon = lon

                    
                    geom_type = geom.get("type", "Point")

                    result = conn.execute(
                        text("""
                            SELECT id FROM geometry_type
                            WHERE type = :type
                        """),
                        {"type": geom_type}
                    )

                    row = result.fetchone()

                    if row:
                        type_id = row[0]
                    else:
                        type_id = conn.execute(
                            text("""
                                INSERT INTO geometry_type (type)
                                VALUES (:type)
                                RETURNING id
                            """),
                            {"type": geom_type}
                        ).scalar()

                    
                    result = conn.execute(
                        text("""
                            INSERT INTO geometry (
                                latitude, longitude, type_id,
                                magnitude, unit, measure_date
                            )
                            VALUES (
                                :lat, :lon, :type_id,
                                NULL, NULL, :date
                            )
                            RETURNING id
                        """),
                        {
                            "lat": lat,
                            "lon": lon,
                            "type_id": type_id,
                            "date": geom.get("date")
                        }
                    )

                    geometry_id = result.scalar()

                    conn.execute(
                        text("""
                            INSERT INTO event_geometry (
                                event_id, geometry_id
                            )
                            VALUES (:event_id, :geometry_id)
                            ON CONFLICT DO NOTHING
                        """),
                        {
                            "event_id": event_id,
                            "geometry_id": geometry_id
                        }
                    )
                

                
                for source in event.get("sources", []):
                    result = conn.execute(
                        text("""
                            SELECT id
                            FROM source
                            WHERE abbreviation = :title
                        """),
                        {
                            "title": source["id"]
                        }
                    )

                source_id = result.scalar()

                if source_id is not None:
                    conn.execute(
                    text("""
                        INSERT INTO event_source (
                            event_id,
                            source_id
                        )
                        VALUES (
                            :event_id,
                            :source_id
                        )
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        "event_id": event_id,
                        "source_id": source_id
                    }
                )

                for category in event.get("categories", []):

                    result = conn.execute(
                        text("""
                            SELECT id
                            FROM category
                            WHERE title = :title
                        """),
                        {
                            "title": category["title"]
                        }
                    )

    
                category_id = result.scalar()

                if category_id is not None:

                    conn.execute(
                    text("""
                        INSERT INTO event_category (
                        event_id,
                        category_id
                        )
                        VALUES (
                        :event_id,
                        :category_id
                        )
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        "event_id": event_id,
                        "category_id": category_id
                    }
                )
                    
                    
                    
                if last_lat is not None and last_lon is not None:
                    location = rg.get((last_lat, last_lon))[0]

                conn.execute(
                    text("""
                        INSERT INTO event_location (
                            event_id,
                            country_code,
                            country,
                            state,
                            city
                        )
                        VALUES (
                            :event_id,
                            :country_code,
                            :country,
                            :state,
                            :city
                        )
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        "event_id": event_id,
                        "country_code": location.get("country_code"),
                        "country": location.get("country"),
                        "state": location.get("state"),
                        "city": location.get("city")
                    }
                )



            print(f"[INFO] Zapisano event {event_id}")

        conn.commit()
        print("[INFO] Import zakończony")

    except SQLAlchemyError as e:
        print(f"[ERROR] {e}")







if __name__ == "__main__":
    pass




