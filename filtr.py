import pandas as pd
from __future__ import annotations
from typing import Any
from time import sleep
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import reverse_geocode as rg
import requests

def event_category(category, conn):
    if not isinstance(category, str):
        return None

    query = f"""
    SELECT
        e.id,
        e.title AS event_title,
        e.start_date,
        e.end_date,
        c.title AS category
    FROM event e
    JOIN event_category ec
        ON e.id = ec.event_id
    JOIN category c
        ON ec.category_id = c.id
    WHERE c.title = %s
    ORDER BY e.start_date DESC
    """

    return pd.read_sql(query, con=conn, params=[category])

def event_country(country, conn):
    if not isinstance(country, str):
        return None

    query = """
    SELECT
        e.id,
        e.title AS event_title,
        el.country,
        el.state,
        el.city,
        e.start_date,
        e.end_date
    FROM event e
    JOIN event_location el ON e.id = el.event_id
    WHERE el.country = %s
    ORDER BY e.start_date DESC
    """

    return pd.read_sql(query, con=conn, params=[country])

def event_city(city, conn):
    if not isinstance(city, str):
        return None

    query = """
    SELECT
        e.id,
        e.title AS event_title,
        el.country,
        el.state,
        el.city,
        e.start_date
    FROM event e
    JOIN event_location el ON e.id = el.event_id
    WHERE el.city = %s
    ORDER BY e.start_date DESC
    """

    return pd.read_sql(query, con=conn, params=[city])

def event_source(source_title, conn):
    if not isinstance(source_title, str):
        return None

    query = """
    SELECT
        e.id,
        e.title AS event_title,
        s.title AS source_title,
        s.abbreviation,
        e.start_date
    FROM event e
    JOIN event_source es ON e.id = es.event_id
    JOIN source s ON es.source_id = s.id
    WHERE s.title = %s
    ORDER BY e.start_date DESC
    """

    return pd.read_sql(query, con=conn, params=[source_title])

def event_geometry_type(geometry_type, conn):
    if not isinstance(geometry_type, str):
        return None

    query = """
    SELECT
        e.id,
        e.title AS event_title,
        gt.type AS geometry_type,
        g.latitude,
        g.longitude,
        g.measure_date
    FROM event e
    JOIN event_geometry eg ON e.id = eg.event_id
    JOIN geometry g ON eg.geometry_id = g.id
    JOIN geometry_type gt ON g.type_id = gt.id
    WHERE gt.type = %s
    ORDER BY g.measure_date DESC
    """

    return pd.read_sql(query, con=conn, params=[geometry_type])

def event_after_date(date, conn):
    if not isinstance(date, str):
        return None

    query = """
    SELECT
        id,
        title,
        start_date,
        end_date
    FROM event
    WHERE start_date >= %s
    ORDER BY start_date DESC
    """

    return pd.read_sql(query, con=conn, params=[date])

def event_unit(unit, conn):
    if not isinstance(unit, str):
        return None

    query = """
    SELECT
        e.id,
        e.title AS event_title,
        g.magnitude,
        g.unit,
        g.measure_date
    FROM event e
    JOIN event_geometry eg ON e.id = eg.event_id
    JOIN geometry g ON eg.geometry_id = g.id
    WHERE g.unit = %s
    ORDER BY g.measure_date DESC
    """

    return pd.read_sql(query, con=conn, params=[unit])

def category_latest_events(category, conn):
    if not isinstance(category, str):
        return None

    query = """
    SELECT
        e.id,
        e.title AS event_title,
        c.title AS category,
        e.start_date,
        e.end_date
    FROM event e
    JOIN event_category ec
        ON e.id = ec.event_id
    JOIN category c
        ON ec.category_id = c.id
    WHERE c.title = %s
    ORDER BY e.start_date DESC
    LIMIT 20
    """

    return pd.read_sql(query, con=conn, params=[category])

def event_status(status, conn):
    if not isinstance(status, str):
        return None

    if status not in ["active", "closed"]:
        return None

    if status == "active":
        query = """
        SELECT
            id,
            title,
            start_date,
            end_date
        FROM event
        WHERE end_date IS NULL
        ORDER BY start_date DESC
        """
    else:
        query = """
        SELECT
            id,
            title,
            start_date,
            end_date
        FROM event
        WHERE end_date IS NOT NULL
        ORDER BY end_date DESC
        """

    return pd.read_sql(query, con=conn)

def event_country_category(country, category, conn):
    if not isinstance(country, str):
        return None

    if not isinstance(category, str):
        return None

    query = """
    SELECT
        e.id,
        e.title AS event_title,
        el.country,
        el.city,
        c.title AS category,
        e.start_date
    FROM event e
    JOIN event_location el ON e.id = el.event_id
    JOIN event_category ec ON e.id = ec.event_id
    JOIN category c ON ec.category_id = c.id
    WHERE el.country = %s
    AND c.title = %s
    ORDER BY e.start_date DESC
    """

    return pd.read_sql(query, con=conn, params=[country, category])


    