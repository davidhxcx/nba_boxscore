import sqlite3
import json
from datetime import datetime

DB_PATH = "nba_games.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode=WAL;")
    c.execute("""
        CREATE TABLE IF NOT EXISTS games (
            game_id TEXT,
            date TEXT,
            data TEXT,
            PRIMARY KEY (game_id, date)
        )
    """)
    conn.commit()
    conn.close()

def save_game(game_id, date, game_data):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode=WAL;")
    # Tente atualizar primeiro
    c.execute("""
        UPDATE games SET data = ? WHERE game_id = ? AND date = ?
    """, (json.dumps(game_data), game_id, date))
    if c.rowcount == 0:
        # Se não atualizou nada, insere
        c.execute("""
            INSERT INTO games (game_id, date, data) VALUES (?, ?, ?)
        """, (game_id, date, json.dumps(game_data)))
    conn.commit()
    conn.close()

def get_games_by_date(date):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode=WAL;")
    c.execute("SELECT data FROM games WHERE date = ?", (date,))
    rows = c.fetchall()
    conn.close()
    return [json.loads(row[0]) for row in rows]

def get_game(game_id):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode=WAL;")
    c.execute("SELECT data FROM games WHERE game_id = ?", (game_id,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None