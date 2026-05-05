# MVP
<!-- Badges — sostituisci GroupRubberDuck/MVP con il tuo username/MVP e main con main o develop -->
![CI](https://github.com/GroupRubberDuck/MVP/actions/workflows/ci.yml/badge.svg?main=main)
![Coverage](https://raw.githubusercontent.com/GroupRubberDuck/MVP/main/badges/coverage.svg)
![Tests](https://raw.githubusercontent.com/GroupRubberDuck/MVP/main/badges/tests.svg)
![Ruff](https://raw.githubusercontent.com/GroupRubberDuck/MVP/main/badges/ruff.svg)
 



Per avviare l'applicazione è sufficiente aver docker e docker compose installati, aver impostato le due variabili di ambiente `DB_USERNAME` e `DB_PASSWORD`, ed eseguire il seguente comando:
```bash
docker compose up --build -d
```
L'applicazione sarà quindi accessibile attraverso il browser all'indirizzo [http://localhost:8080](http://localhost:8080).

## Sviluppo
Per lo sviluppo è necessario avere docker e docker compose installati ed eseguire il seguente comando per avviare tutti i servizi:
```bash
docker compose -f docker-compose.devel.yaml up --build -d
```

I seguenti servizi saranno avviati ai rispettivi url:
- Flask in modalità debug: http://localhost:5000
- MongoDB: mongo://localhost:27017
- Mongo Express: http://localhost:8081
- Vite build automatica continua

Per fermare tutti i servizi è sufficiente eseguire:
```bash
docker compose -f docker-compose.devel.yaml down
```

### Validazione
```bash
poetry run mypy .
poetry run ruff check .
poetry run pytest
poetry run strictdoc export .
```

### Documentazione
- [StrictDoc](https://strictdoc.readthedocs.io/en/stable/stable/docs/strictdoc_01_user_guide.html)
- [Flask](https://flask.palletsprojects.com/en/stable/)
- [mypy](https://mypy.readthedocs.io/en/stable/getting_started.html)
