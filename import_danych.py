import sqlite3
import requests
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import  reverse_geocode as  rg
from fetch_api import fetch_events
from datetime import datetime, timezone

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

    records_saved = 0
    
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
            records_saved +=1
            
            last_lat = None
            last_lon = None

            for geom in event["geometry"]:
                coords = geom.get("coordinates", [None, None])
                lon = coords[0]
                lat = coords[1]
                measure_date = geom.get("date")

              
                if lon is not None and lon > 180:
                    lon = lon - 360
                
                last_lat = lat
                last_lon = lon
                
                geom_type = geom.get("type", "Point")

                existing_geom = conn.execute(
                    text("""
                        SELECT g.id 
                        FROM geometry g
                        JOIN event_geometry eg ON g.id = eg.geometry_id
                        WHERE eg.event_id = :event_id AND g.measure_date = :measure_date
                    """),
                    {
                        "event_id": event_id,
                        "measure_date": measure_date
                    }
                ).scalar()
            

                
                if existing_geom is not None:
                    continue

                type_id = conn.execute(
                    text("SELECT id FROM geometry_type WHERE type = :type"),
                    {"type": geom_type}
                ).scalar()
                records_saved += 1

                if not type_id:
                    type_id = conn.execute(
                        text("""
                            INSERT INTO geometry_type (type)
                            VALUES (:type)
                            RETURNING id
                        """),
                        {"type": geom_type}
                    ).scalar()
                    records_saved += 1

               
                geometry_id = conn.execute(
                    text("""
                        INSERT INTO geometry (
                            latitude, longitude, type_id,
                            magnitude, unit, measure_date
                        )
                        VALUES (
                            :lat, :lon, :type_id,
                            :magnitude, :unit, :date
                        )
                        RETURNING id
                    """),
                    {
                        "lat": lat,
                        "lon": lon,
                        "type_id": type_id,
                        "magnitude": geom.get("magnitudeValue"),
                        "unit": geom.get("magnitudeUnit"),
                        "date": measure_date
                    }
                ).scalar()
                records_saved += 1

       
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
                records_saved += 1
            

            
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
                records_saved += 1
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
                records_saved+=1

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
                records_saved +=1
                
                
            if last_lat is not None and last_lon is not None:
                location = rg.get((last_lat, last_lon))

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
            records_saved += 1


        print(f"[INFO] Zapisano event {event_id}")

    conn.commit()
    print("[INFO] Import zakończony")


    return records_saved


def write_import_log(
    conn: sqlite3.Connection,
    *,
    imported_at: str,
    records_received: int,
    records_saved: int,
    status: str,
    error_message: str | None = None,
    api_url
) -> None:
    """Zapisuje informację o przebiegu importu do tabeli import_log."""

    conn.execute(
                text(
                    '''
                    INSERT INTO import_log (
                        imported_at,
                        apiname,
                        endpoint,
                        records_received,
                        records_saved,
                        status
                    ) VALUES (
                        :imported_at,
                        :api_name,
                        :endpoint,
                        :records_received,
                        :records_saved,
                        :status
                    )
                    '''
                ),
                  {
                    "imported_at": imported_at,
                    "api_name": api_url,  
                    "endpoint": "NASA EONERT API",  
                    "records_received": records_received,
                    "records_saved": records_saved,
                    "status": status
                }
                )
    
    conn.commit()

def run_import(engine, limit, days):
    events = fetch_events(days, limit)
    records_saved = 0
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    api_url = "https://eonet.gsfc.nasa.gov/api/v3/events"
    try:
        records_saved = import_event(events, engine)
        with engine.begin() as conn:
            write_import_log(
                conn,
                imported_at=timestamp,
                records_received=len(events),
                records_saved=records_saved,
                status="SUCCESS",
                api_url="https://eonet.gsfc.nasa.gov/api/v3/events"
            )
    except Exception as e:
        with engine.begin() as conn:
            write_import_log(
                conn,
                imported_at=timestamp,
                records_received=len(events),
                records_saved=records_saved,
                status="ERROR",
                error_message=str(e),
                api_url="https://eonet.gsfc.nasa.gov/api/v3/events"
            )
    return

if __name__ == "__main__":
    pass




