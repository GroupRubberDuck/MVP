#!/bin/sh
# =============================================================================
# watcher.sh — Supervisore per vite build --watch
#
# Risolve i limiti del lancio diretto:
#   1. Auto-restart quando vite.config.js o package.json cambiano
#   2. Auto-restart se Vite crasha (con backoff)
#   3. Errori di compilazione visibili in docker compose logs
#   4. npm install con retry e cache tramite named volume
# =============================================================================

set -e

# ── Configurazione ──────────────────────────────────────────────────────────
WATCH_FILES="vite.config.js package.json"
POLL_INTERVAL=2
MAX_INSTALL_RETRIES=3
CRASH_RESTART_DELAY=3
VITE_PID=""

# ── Output leggibile ────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { printf "${CYAN}[watcher]${NC} %s\n" "$1"; }
log_ok()    { printf "${GREEN}[watcher]${NC} %s\n" "$1"; }
log_warn()  { printf "${YELLOW}[watcher]${NC} %s\n" "$1"; }
log_error() { printf "${RED}[watcher]${NC} %s\n" "$1"; }
log_sep()   { printf "${CYAN}[watcher]${NC} ──────────────────────────────────────────\n"; }

# ── Cleanup su shutdown ─────────────────────────────────────────────────────
cleanup() {
    log_info "Shutdown richiesto..."
    kill_vite
    exit 0
}
trap cleanup SIGTERM SIGINT

kill_vite() {
    if [ -n "$VITE_PID" ] && kill -0 "$VITE_PID" 2>/dev/null; then
        log_info "Termino Vite (PID: $VITE_PID)..."
        kill "$VITE_PID" 2>/dev/null || true
        wait "$VITE_PID" 2>/dev/null || true
        VITE_PID=""
    fi
}

# ── npm install con retry ───────────────────────────────────────────────────
do_install() {
    local attempt=1
    while [ $attempt -le $MAX_INSTALL_RETRIES ]; do
        log_info "npm install (tentativo $attempt/$MAX_INSTALL_RETRIES)..."
        if npm install 2>&1; then
            log_ok "Dipendenze installate"
            return 0
        fi
        log_warn "npm install fallito, riprovo tra 5s..."
        attempt=$((attempt + 1))
        sleep 5
    done
    log_error "npm install fallito dopo $MAX_INSTALL_RETRIES tentativi"
    return 1
}

# ── Checksum dei file di config ──────────────────────────────────────────────
get_config_hash() {
    local hash=""
    for f in $WATCH_FILES; do
        if [ -f "$f" ]; then
            hash="${hash}$(md5sum "$f" 2>/dev/null)"
        fi
    done
    echo "$hash"
}

# ── Avvia Vite ───────────────────────────────────────────────────────────────
start_vite() {
    kill_vite
    log_sep
    log_info "Avvio vite build --watch"
    log_sep

    npx vite build --watch 2>&1 &
    VITE_PID=$!

    sleep 1
    if kill -0 "$VITE_PID" 2>/dev/null; then
        log_ok "Vite avviato (PID: $VITE_PID)"
    else
        log_error "Vite non è partito! Controlla l'output sopra."
        VITE_PID=""
        return 1
    fi
}

# ── Main ─────────────────────────────────────────────────────────────────────
log_sep
log_info "Vue Watcher Supervisor"
log_info "Monitorando: $WATCH_FILES"
log_sep

# Step 1: Installa dipendenze
do_install || { log_error "Impossibile installare le dipendenze. Esco."; exit 1; }

# Step 2: Prima build
start_vite || log_warn "Prima build fallita, continuo a monitorare..."

# Step 3: Loop di monitoraggio
LAST_HASH=$(get_config_hash)

while true; do
    sleep "$POLL_INTERVAL"

    # Controlla se il config è cambiato
    CURRENT_HASH=$(get_config_hash)
    if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
        log_sep
        log_warn "Config modificato — riavvio in corso"
        log_sep
        LAST_HASH="$CURRENT_HASH"

        # Se package.json è cambiato, reinstalla
        do_install || log_warn "npm install fallito, provo comunque..."
        start_vite || log_warn "Restart fallito, riproverò..."
        continue
    fi

    # Controlla che Vite sia ancora vivo
    if [ -n "$VITE_PID" ] && ! kill -0 "$VITE_PID" 2>/dev/null; then
        log_sep
        log_error "Vite è crashato — riavvio tra ${CRASH_RESTART_DELAY}s"
        log_sep
        VITE_PID=""
        sleep "$CRASH_RESTART_DELAY"
        start_vite || log_warn "Restart fallito, riproverò..."
    fi
done
