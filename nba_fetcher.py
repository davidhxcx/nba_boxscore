# Este projeto está licenciado sob a GNU GPLv3 - veja o arquivo LICENSE para detalhes.
from nba_api.live.nba.endpoints import scoreboard, boxscore
import logging
from utils import get_logo_path
from db import save_game
from datetime import datetime
import pytz

logger = logging.getLogger("NBA Boxscore App")

STAT_TRANSLATIONS = {
    "points": "PTS",
    "assists": "AST",
    "reboundsTotal": "REB",
    "reboundsOffensive": "OFF",
    "reboundsDefensive": "DEF",
    "blocks": "BLK",
    "steals": "STL",
    "fieldGoalsMade": "FGM",
    "fieldGoalsAttempted": "FGA",
    "fieldGoalsPercentage": "FG%",
    "threePointersMade": "3PM",
    "threePointersAttempted": "3PA",
    "threePointersPercentage": "3P%",
    "freeThrowsMade": "FTM",
    "freeThrowsAttempted": "FTA",
    "freeThrowsPercentage": "FT%",
    "turnovers": "TO",
    "foulsPersonal": "PF",
    "minutesCalculated": "MIN",
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
    br_tz = pytz.timezone("America/Sao_Paulo")
    game_list = []
    today = datetime.now().strftime("%Y-%m-%d")
    for g in games:
        # Converte o horário do jogo para o Brasil
        game_time_utc = g.get("gameTimeUTC")
        if game_time_utc:
            dt_utc = datetime.strptime(game_time_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
            game_time_br = dt_utc.astimezone(br_tz).strftime("%H:%M")
        else:
            game_time_br = ""
        if g["gameStatus"] == 3:
            status = "Encerrado"
        elif g["gameStatus"] == 2:
            status = "Em andamento"
        else:
            status = "Agendado"
        game_data = {
            "game_id": g["gameId"],
            "home_team": g["homeTeam"]["teamTricode"],
            "away_team": g["awayTeam"]["teamTricode"],
            "home_logo": get_logo_path(g["homeTeam"]["teamTricode"]),
            "away_logo": get_logo_path(g["awayTeam"]["teamTricode"]),
            "home_score": g["homeTeam"].get("score", 0),
            "away_score": g["awayTeam"].get("score", 0),
            "status": status,
            "time": game_time_br
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