function toggleBoxscore(gameId) {
    var boxscoreDiv = document.getElementById('boxscore-' + gameId);
    if (boxscoreDiv.style.display === 'none') {
        boxscoreDiv.style.display = 'block';
        if (!boxscoreDiv.dataset.loaded) {
            fetch('/api/boxscore/' + gameId)
                .then(response => response.text())
                .then(html => {
                    boxscoreDiv.innerHTML = html;
                    boxscoreDiv.dataset.loaded = "1";
                    colorirPlusMinus();
                })
                .catch(() => {
                    boxscoreDiv.innerHTML = "<div style='color:red'>Erro ao carregar boxscore.</div>";
                });
        }
    } else {
        boxscoreDiv.style.display = 'none';
    }
}

function colorirPlusMinus() {
    document.querySelectorAll('.plusminus-row').forEach(function(row) {
        if (row.dataset.zerado === "1") {
            row.style.background = "";
            return;
        }
        var pm = parseInt(row.dataset.plusminus, 10);
        // Defina os limites para o gradiente
        var max = 20, min = -20;
        if (pm > 0) {
            // Verde forte para claro
            var pct = Math.min(pm, max) / max;
            row.style.background = `rgba(67, 160, 71, ${0.15 + pct * 0.45})`;
        } else if (pm < 0) {
            // Vermelho claro para forte
            var pct = Math.max(pm, min) / min;
            row.style.background = `rgba(229, 57, 53, ${0.15 + pct * 0.45})`;
        } else {
            row.style.background = "";
        }
    });
}

// Chame essa função após carregar o boxscore via AJAX
document.addEventListener("DOMContentLoaded", colorirPlusMinus);
document.addEventListener("htmx:afterSwap", colorirPlusMinus); // Se usar htmx
// Ou, se usa fetch, chame colorirPlusMinus() após inserir o HTML do boxscore

// Atualização automática dos boxscores abertos a cada 5 segundos
function updateOpenBoxscores() {
    document.querySelectorAll('.boxscore-content').forEach(function(boxscoreDiv) {
        if (boxscoreDiv.style.display !== "none") {
            const gameId = boxscoreDiv.id.replace('boxscore-', '');
            fetch('/api/boxscore/' + gameId)
                .then(response => response.text())
                .then(html => {
                    boxscoreDiv.innerHTML = html;
                    colorirPlusMinus();
                });
        }
    });
}
setInterval(updateOpenBoxscores, 5000);

// Atualização automática dos placares e status da lista de jogos a cada 5 segundos
function updateGamesList() {
    var dateInput = document.getElementById('date');
    var date = dateInput ? dateInput.value : null;
    fetch('/api/games' + (date ? '?date=' + date : ''))
        .then(response => response.json())
        .then(games => {
            games.forEach(function(game) {
                // Atualiza o placar
                var scoreSpan = document.getElementById('score-' + game.game_id);
                if (scoreSpan) {
                    scoreSpan.textContent = game.home_score + " x " + game.away_score;
                }
                // Atualiza o status
                var statusDiv = document.getElementById('status-' + game.game_id);
                if (statusDiv) {
                    let dotClass = "status-dot ";
                    if (game.status === 'Em andamento') {
                        dotClass += "dot-live";
                    } else if (game.status === 'Encerrado') {
                        dotClass += "dot-finished";
                    } else if (game.status_text && game.status_text.toLowerCase().includes('half')) {
                        dotClass += "dot-halftime";
                    } else {
                        dotClass += "dot-scheduled";
                    }
                    let statusText = (game.status_text && game.status_text.toLowerCase().includes('half')) ? "Intervalo" : game.status;
                    let timeHtml = game.time ? `<span class="game-time">${game.time}</span>` : "";
                    statusDiv.innerHTML = `<span class="${dotClass}"></span><strong>Status:</strong> ${statusText} ${timeHtml}`;
                }
            });
        });
}
setInterval(updateGamesList, 5000);