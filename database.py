import sqlite3
import json

conn = sqlite3.connect(
    "barbershop.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS data (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

conn.commit()


def save_data(key, value):

    json_value = json.dumps(value)

    cursor.execute("""
    INSERT OR REPLACE INTO data (
        key,
        value
    )
    VALUES (?, ?)
    """, (
        key,
        json_value
    ))

    conn.commit()


def load_data(key):

    cursor.execute("""
    SELECT value
    FROM data
    WHERE key = ?
    """, (key,))

    row = cursor.fetchone()

    if not row:
        return {}

    return json.loads(row[0])