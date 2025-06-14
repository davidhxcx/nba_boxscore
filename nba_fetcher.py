# Este projeto está licenciado sob a GNU GPLv3 - veja o arquivo LICENSE para detalhes.
from nba_api.live.nba.endpoints import scoreboard, boxscore
import logging
from utils import get_logo_path
from db import save_game
from datetime import datetime

logger = logging.getLogger("NBA Boxscore App")

STAT_TRANSLATIONS = {
    "points": "Pontos",
    "assists": "Assistências",
    "reboundsTotal": "Rebotes",
    "reboundsOffensive": "Reb. Ofensivos",
    "reboundsDefensive": "Reb. Defensivos",
    "blocks": "Tocos",
    "steals": "Roubos",
    "fieldGoalsMade": "FG Convertidos",
    "fieldGoalsAttempted": "FG Tentados",
    "fieldGoalsPercentage": "FG %",
    "threePointersMade": "3PT Convertidos",
    "threePointersAttempted": "3PT Tentados",
    "threePointersPercentage": "3PT %",
    "freeThrowsMade": "Lances Livres Convertidos",
    "freeThrowsAttempted": "Lances Livres Tentados",
    "freeThrowsPercentage": "LL %",
    "turnovers": "Erros",
    "foulsPersonal": "Faltas",
    "minutesCalculated": "Minutos",
}

STAT_ORDER = [
    "points",
    "assists",
    "reboundsTotal",
    "reboundsOffensive",
    "reboundsDefensive",
    "blocks",
    "steals",
    "fieldGoalsMade",
    "fieldGoalsAttempted",
    "fieldGoalsPercentage",
    "threePointersMade",
    "threePointersAttempted",
    "threePointersPercentage",
    "freeThrowsMade",
    "freeThrowsAttempted",
    "freeThrowsPercentage",
    "turnovers",
    "foulsPersonal",
    "minutesCalculated",
]


def get_today_games():
    sb = scoreboard.ScoreBoard()
    games = sb.get_dict()["scoreboard"]["games"]
    today = datetime.now().strftime("%Y-%m-%d")
    game_list = []
    for g in games:
        game_data = {
            "game_id": g["gameId"],
            "home_team": g["homeTeam"]["teamTricode"],
            "away_team": g["awayTeam"]["teamTricode"],
            "home_logo": get_logo_path(g["homeTeam"]["teamTricode"]),
            "away_logo": get_logo_path(g["awayTeam"]["teamTricode"]),
            "home_score": g["homeTeam"].get("score", 0),
            "away_score": g["awayTeam"].get("score", 0)
        }
        save_game(g["gameId"], today, game_data)
        game_list.append(game_data)
    return game_list

def get_boxscore(game_id):
    try:
        bs = boxscore.BoxScore(game_id)
        game_data = bs.game.get_dict()
        home_team = game_data.get('homeTeam', {})
        away_team = game_data.get('awayTeam', {})
        home_tricode = home_team.get('teamTricode', 'HOME')
        away_tricode = away_team.get('teamTricode', 'AWAY')
        home_score = home_team.get('score', 0)
        away_score = away_team.get('score', 0)
        home_players = home_team.get('players', [])
        away_players = away_team.get('players', [])
        for p in home_players:
            p['teamTricode'] = home_tricode
            p['team_logo'] = get_logo_path(home_tricode)
            stats = p.get('statistics', {})
            for k, v in stats.items():
                p[k] = v
        for p in away_players:
            p['teamTricode'] = away_tricode
            p['team_logo'] = get_logo_path(away_tricode)
            stats = p.get('statistics', {})
            for k, v in stats.items():
                p[k] = v
        # Filtra apenas as estatísticas desejadas
        stat_keys = [k for k in STAT_ORDER if any(k in player for player in home_players + away_players)]
        return {
            "home_team": home_tricode,
            "away_team": away_tricode,
            "home_score": home_score,
            "away_score": away_score,
            "home_players": home_players,
            "away_players": away_players,
            "stat_keys": stat_keys,
            "stat_translations": STAT_TRANSLATIONS,
        }
    except Exception as e:
        logger.error(f"Erro ao buscar boxscore para o jogo {game_id}: {e}")
        return {
            "home_team": "",
            "away_team": "",
            "home_score": 0,
            "away_score": 0,
            "home_players": [],
            "away_players": [],
            "stat_keys": [],
            "stat_translations": STAT_TRANSLATIONS,
        }