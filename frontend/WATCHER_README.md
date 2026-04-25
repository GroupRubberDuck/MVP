# Frontend Watcher — Guida Operativa

## Modalità disponibili

### 1. Watch mode (default) — `vite build --watch`

Compila i `.vue` e li copia in `backend/static/vue/` ad ogni modifica.
Flask li serve come file statici normali. Nessuna modifica ai template necessaria.

```bash
# Avvia tutto (backend + mongo + mongo-express + watcher)
docker compose -f docker-compose.devel.yaml up

# Oppure esplicitamente
docker compose -f docker-compose.devel.yaml --profile watch up
```

**Vedere i log del watcher:**
```bash
docker compose -f docker-compose.devel.yaml logs -f vue-watcher
```

**Cosa succede automaticamente:**
- Modifichi un `.vue` → Vite ricompila → Flask serve il file aggiornato → refresh manuale nel browser
- Modifichi `vite.config.js` → il supervisore rileva il cambio → killa Vite → rilancia `vite build --watch`
- Modifichi `package.json` → rileva il cambio → riesegue `npm install` → rilancia Vite
- Vite crasha → il supervisore lo rilancia dopo 3 secondi

### 2. Dev server mode — Vite HMR

Avvia il dev server Vite sulla porta 5173 con Hot Module Replacement.
Il browser carica gli asset direttamente da Vite → aggiornamento istantaneo senza refresh.

```bash
docker compose -f docker-compose.devel.yaml --profile vite-dev up
```

> **Nota:** questa modalità richiede che i template Flask puntino a `http://localhost:5173`
> per gli asset Vue in dev. Vedi la sezione "Integrazione template Flask" qui sotto.

## Integrazione template Flask (solo per vite-dev mode)

Per usare il dev server, il template base di Flask deve distinguere tra dev e produzione.
Esempio con Jinja2:

```html
{% if config.VITE_DEV_MODE %}
  <!-- Dev: carica dal dev server Vite con HMR -->
  <script type="module" src="http://localhost:5173/@vite/client"></script>
  <script type="module" src="http://localhost:5173/src/main.js"></script>
{% else %}
  <!-- Prod/Watch: carica i file compilati -->
  <script type="module" src="/static/vue/helloworld.js"></script>
  <link rel="stylesheet" href="/static/vue/helloworld.css">
{% endif %}
```

Nel `create_app` di Flask, esponi la variabile:
```python
import os

def create_app():
    app = Flask(__name__)
    app.config['VITE_DEV_MODE'] = os.environ.get('VITE_DEV_MODE', 'false') == 'true'
    return app
```

## Troubleshooting

**Il watcher non rileva le modifiche:**
```bash
# Controlla che il container sia attivo
docker compose -f docker-compose.devel.yaml ps vue_watcher

# Guarda i log
docker compose -f docker-compose.devel.yaml logs -f vue-watcher
```

**Errori di compilazione:**
Sono visibili direttamente nei log del watcher. Il supervisore NON killa Vite
per errori di compilazione — Vite continua a girare e riprova al prossimo salvataggio.

**Dipendenze stale / problemi con node_modules:**
```bash
# Resetta il volume dei node_modules
docker compose -f docker-compose.devel.yaml down -v
docker compose -f docker-compose.devel.yaml up
```

**Il watcher parte ma i file non appaiono in backend/static/vue/:**
Verifica che il path `outDir` in `vite.config.js` sia `'../backend/static/vue'`.
Nel container, la struttura è `/app/frontend/` (sorgenti) e `/app/backend/static/vue/` (output).
