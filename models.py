# models.py
import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            team TEXT,
            points INTEGER,
            rebounds INTEGER,
            assists INTEGER,
            game_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_stats(players, game_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    for p in players:
        stats = p.get('statistics', {})
        c.execute('''
            INSERT INTO player_stats (player_name, team, points, rebounds, assists, game_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            p['name'],
            p['teamTricode'],
            stats.get('points', 0),
            stats.get('rebounds', 0),
            stats.get('assists', 0),
            game_id
        ))
    conn.commit()
    conn.close()
