import sqlite3
import json
from datetime import datetime

DB_PATH = "nba_games.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS games (
            game_id TEXT PRIMARY KEY,
            date TEXT,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_game(game_id, date, data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO games (game_id, date, data)
        VALUES (?, ?, ?)
    """, (game_id, date, json.dumps(data)))
    conn.commit()
    conn.close()

def get_games_by_date(date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT data FROM games WHERE date = ?", (date,))
    rows = c.fetchall()
    conn.close()
    return [json.loads(row[0]) for row in rows]

def get_game(game_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT data FROM games WHERE game_id = ?", (game_id,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None