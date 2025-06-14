# NBA Boxscore Web App

> **Aviso:** Este projeto não é afiliado à NBA. Todos os logos, nomes e marcas são propriedade de seus respectivos detentores. O objetivo deste projeto é apenas educacional e por admiração ao basquete.

Este projeto é uma aplicação web desenvolvida em Python com FastAPI para exibir jogos, estatísticas e histórico de jogadores da NBA. A interface é moderna, responsiva e permite consultar partidas por data, estatísticas de jogadores ativos e históricos, além de exibir informações detalhadas de cada partida.

## Funcionalidades

- **Jogos do Dia:** Exibe todos os jogos do dia selecionado, com placar, logos dos times e visual centralizado.
- **Consulta por Data:** Permite escolher qualquer data para visualizar os jogos salvos daquele dia.
- **Boxscore Detalhado:** Ao clicar em um jogo, exibe todas as estatísticas dos jogadores das duas equipes, com visual padronizado.
- **Jogadores Históricos:** Busca e lista todos os jogadores que já atuaram na NBA (ativos e inativos), com filtro por nome.
- **Estatísticas de Carreira:** Ao clicar em um jogador histórico, exibe todas as estatísticas de carreira por temporada.
- **Background Personalizado:** Imagem de fundo customizável via `/static/background/background.jpg`.
- **Favicon Personalizado:** Ícone da aba customizável via `/static/basketball.ico`.
- **Botão de Voltar:** Navegação fácil entre páginas.
- **Histórico Local:** Jogos são salvos localmente em banco SQLite para consulta futura.
- **Aviso de Direitos Autorais:** Rodapé com aviso sobre uso de logos e marcas.

## Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [nba_api](https://github.com/swar/nba_api)
- [pandas](https://pandas.pydata.org/)
- [requests](https://requests.readthedocs.io/)
- SQLite (banco de dados local)
- HTML5, CSS3

## Como rodar localmente

1. **Clone o repositório:**
   ```
   git clone https://github.com/seuusuario/nba_boxscore.git
   cd nba_boxscore
   ```

2. **Instale as dependências:**
   ```
   pip install -r requirements.txt
   ```

3. **(Opcional) Coloque sua imagem de fundo em `static/background/background.jpg`.**
4. **(Opcional) Coloque seu favicon em `static/basketball.ico`.**

5. **Inicie a aplicação:**
   ```
   uvicorn main:app --reload
   ```

6. **Acesse no navegador:**  
   [http://localhost:8000](http://localhost:8000)

## Estrutura de Pastas

```
nba_boxscore/
├── main.py
├── nba_fetcher.py
├── db.py
├── requirements.txt
├── LICENSE
├── static/
│   ├── style.css
│   ├── basketball.ico
│   └── background/
│       └── background.jpg
├── templates/
│   ├── index.html
│   ├── boxscore.html
│   ├── historical_players.html
│   ├── historical_player_stats.html
├── utils.py
```

## Licença

Este projeto está licenciado sob a [GNU General Public License v3.0](LICENSE).

## Aviso

> **Aviso:** Este projeto não é afiliado à NBA. Todos os logos, nomes e marcas são propriedade de seus respectivos detentores. O objetivo deste projeto é apenas educacional e por admiração ao basquete.

## Créditos

- Logos dos times: ESPN CDN
- Dados da NBA: [nba_api](https://github.com/swar/nba_api)
- Desenvolvido por [Seu Nome ou Usuário]

---

Sinta-se à vontade para contribuir, sugerir melhorias ou relatar