# Este projeto está licenciado sob a GNU GPLv3 - veja o arquivo LICENSE para detalhes.
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from nba_api.stats.endpoints import leaguedashplayerstats
from fastapi.staticfiles import StaticFiles
from nba_fetcher import get_today_games, get_boxscore
from models import init_db, save_stats
from db import get_games_by_date
from datetime import datetime
from nba_api.stats.endpoints import commonallplayers
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.library.parameters import SeasonAll
from nba_api.stats.library.http import NBAStatsHTTP
from db import init_db
import uvicorn
import logging
import pandas as pd

templates = Jinja2Templates(directory="templates")

NBAStatsHTTP.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/'
}

init_db()

# Adicione estas linhas para configurar o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NBA Boxscore App")


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request, date: str = None):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    games = get_games_by_date(date)
    today = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "games": games, "today": today, "date": date}
    )


@app.get("/historical_players")
async def historical_players(request: Request, search: str = ""):
    try:
        players_df = commonallplayers.CommonAllPlayers(is_only_current_season=0, timeout=10).get_data_frames()[0]
        if search:
            players_df = players_df[players_df["DISPLAY_FIRST_LAST"].str.contains(search, case=False, na=False)]
        players = players_df.to_dict(orient="records")
        error_message = ""
    except Exception as e:
        players = []
        error_message = "Não foi possível buscar os jogadores históricos no momento. Tente novamente mais tarde."
    return templates.TemplateResponse(
        "historical_players.html",
        {
            "request": request,
            "players": players,
            "search": search,
            "error_message": error_message
        }
    )

@app.get("/historical_player_stats/{player_id}")
async def historical_player_stats(request: Request, player_id: int):
    stats_df = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]
    player_name = ""
    if not stats_df.empty:
        player_name = stats_df.iloc[0].get("PLAYER_NAME", "")
    stat_keys = ["SEASON_ID", "TEAM_ABBREVIATION", "GP", "PTS", "REB", "AST", "STL", "BLK", "TOV", "FG_PCT", "FG3_PCT", "FT_PCT"]
    stat_translations = {
        "SEASON_ID": "Temporada",
        "TEAM_ABBREVIATION": "Time",
        "GP": "Jogos",
        "PTS": "Pontos",
        "REB": "Rebotes",
        "AST": "Assistências",
        "STL": "Roubos",
        "BLK": "Tocos",
        "TOV": "Erros",
        "FG_PCT": "FG %",
        "FG3_PCT": "3PT %",
        "FT_PCT": "LL %",
    }
    stats = stats_df.to_dict(orient="records")
    return templates.TemplateResponse(
        "historical_player_stats.html",
        {
            "request": request,
            "stats": stats,
            "stat_keys": stat_keys,
            "stat_translations": stat_translations,
            "player_name": player_name
        }
    )

@app.get("/")
async def home(request: Request):
    logger.info("Buscando jogos do dia...")
    games = get_today_games()
    return templates.TemplateResponse("index.html", {"request": request, "games": games})

@app.get("/boxscore/{game_id}")
async def boxscore(request: Request, game_id: str):
    logger.info(f"Buscando boxscore para o jogo {game_id}...")
    boxscore_data = get_boxscore(game_id)
    return templates.TemplateResponse(
        "boxscore.html",
        {
            "request": request,
            "home_team": boxscore_data["home_team"],
            "away_team": boxscore_data["away_team"],
            "home_score": boxscore_data["home_score"],
            "away_score": boxscore_data["away_score"],
            "home_players": boxscore_data["home_players"],
            "away_players": boxscore_data["away_players"],
            "stat_keys": boxscore_data["stat_keys"],
            "stat_translations": boxscore_data["stat_translations"],
        }
    )

    # Proteger contra falta da chave teamTricode antes de salvar
    players_filtered = [p for p in players if 'teamTricode' in p]

    save_stats(players_filtered, game_id)

    # Organizar jogadores por time para a view
    team_players = {}
    for p in players_filtered:
        team = p.get('teamTricode', 'Unknown')
        if team not in team_players:
            team_players[team] = []
        team_players[team].append(p)

    return templates.TemplateResponse("boxscore.html", {
        "request": request,
        "team_players": team_players,
        "game_id": game_id
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

