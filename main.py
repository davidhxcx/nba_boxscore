# Este projeto está licenciado sob a GNU GPLv3 - veja o arquivo LICENSE para detalhes.
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from nba_api.stats.endpoints import commonallplayers, playercareerstats
from nba_api.stats.static import teams
from nba_api.stats.library.http import NBAStatsHTTP
from nba_fetcher import get_today_games, get_boxscore, STAT_TRANSLATIONS, STAT_FULL_NAMES
from db import get_games_by_date, init_db
from models import save_stats
from datetime import datetime
import logging
import uvicorn

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NBA Boxscore App")

# Configuração do FastAPI e templates
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Headers para NBA API
NBAStatsHTTP.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/'
}

init_db()

def get_team_list():
    # Retorna uma lista de dicionários com 'abbreviation' e 'full_name'
    return sorted(
        [{"abbreviation": t["abbreviation"], "full_name": t["full_name"]} for t in teams.get_teams()],
        key=lambda x: x["full_name"]
    )

@app.get("/api/boxscore/{game_id}", response_class=HTMLResponse)
async def api_boxscore(request: Request, game_id: str):
    boxscore = get_boxscore(game_id)
    return templates.TemplateResponse(
        "boxscore_partial.html",
        {
            "home_team": boxscore["home_team"],
            "away_team": boxscore["away_team"],
            "home_score": boxscore["home_score"],
            "away_score": boxscore["away_score"],
            "home_players": boxscore["home_players"],
            "away_players": boxscore["away_players"],
            "stat_keys": boxscore["stat_keys"],
            "stat_translations": STAT_TRANSLATIONS,
            "stat_full_names": STAT_FULL_NAMES,
            "request": request
        }
    )

@app.get("/api/games")
async def api_games(date: str = None, team: str = None):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    if date == datetime.now().strftime("%Y-%m-%d"):
        get_today_games()
    games = get_games_by_date(date)
    if team:
        games = [g for g in games if g["home_team"] == team or g["away_team"] == team]
    return JSONResponse(games)

@app.get("/")
async def index(request: Request, date: str = None, team: str = None):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    # Sempre busca da API e salva no banco se for hoje
    if date == datetime.now().strftime("%Y-%m-%d"):
        get_today_games()
    games = get_games_by_date(date)
    if team:
        games = [g for g in games if g["home_team"] == team or g["away_team"] == team]
    today = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
    team_list = get_team_list()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "games": games, "today": today, "date": date, "team": team, "team_list": team_list}
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)