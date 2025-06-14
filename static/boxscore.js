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