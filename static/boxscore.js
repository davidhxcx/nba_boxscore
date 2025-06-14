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