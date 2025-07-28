import os
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise ValueError("DATABASE_URL not set")
    parsed = urlparse(url)
    dbname = parsed.path[1:]
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port
    return psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            text TEXT,
            aspects TEXT,
            emotions TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_review(text, aspects, emotions):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO reviews (text, aspects, emotions) VALUES (%s, %s, %s)", (text, ','.join(aspects), ','.join(emotions)))
    conn.commit()
    cur.close()
    conn.close()

def get_dynamic_reviews():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, text, aspects, emotions FROM reviews ORDER BY timestamp DESC")
    reviews = cur.fetchall()
    cur.close()
    conn.close()
    return [{'id': r[0], 'text': r[1], 'aspects': r[2].split(',') if r[2] else [], 'emotions': r[3].split(',') if r[3] else []} for r in reviews]