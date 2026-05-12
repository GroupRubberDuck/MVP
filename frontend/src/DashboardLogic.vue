<template>
  <!-- Componente invisibile che fa da "cervello" alla Dashboard -->
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';

// 1. Recuperiamo il sessionId dall'URL in modo sicuro
const pathParts = window.location.pathname.split('/');
const sessionIndex = pathParts.indexOf('sessions');
const sessionId = sessionIndex !== -1 ? pathParts[sessionIndex + 1] : null;

// 2. Logica per bloccare la chiusura della scheda o il refresh (Popup di Sistema)
const handleBeforeUnload = (event) => {
  const message = "Valutazione in corso. Se esci ora, i dati non salvati andranno persi.";
  event.preventDefault();
  event.returnValue = message; // Il browser ignorerà questo testo, ma serve per attivare il suo blocco
  return message;
};

// 3. Funzione per rimuovere i blocchi (da usare prima di un redirect "legale")
const allowExit = () => {
  window.removeEventListener('beforeunload', handleBeforeUnload);
  window.onpopstate = null; // Rimuove il blocco del tasto indietro
};

// 4. Azioni collegate ai pulsanti della Dashboard 
const dashboardAction = {
  // SALVA (PUT)
save: async () => {
    if (!sessionId) return alert("Errore: ID sessione non trovato.");
    
    try {
      const response = await fetch(`/sessions/${sessionId}/commit`, { method: 'POST' });
      
      if (!response.ok) {
        // Estrai il corpo della risposta come testo
        const errorText = await response.text(); 
        throw new Error(`Errore nel salvataggio sul server: ${errorText}`);
      }
      
      alert("Sessione salvata con successo!");
    } catch (e) {
      alert("Impossibile salvare: " + e.message);
    }
  },

  // CHIUDI (DELETE)
  close: async () => {
    if (!sessionId) return alert("Errore: ID sessione non trovato.");
    
    if (confirm("Sei sicuro di voler chiudere la sessione? I dati non salvati andranno persi.")) {
      try {
        const response = await fetch(`/sessions/${sessionId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error("Errore nella chiusura della sessione sul server.");

        allowExit(); // Rimuoviamo il lucchetto prima di uscire
        window.location.href = "/devices"; // Reindirizzamento alla lista dispositivi
      } catch (e) {
        alert("Errore durante la chiusura: " + e.message);
      }
    }
  },

  // GENERA REPORT
  generateReport: () => {
    // Prima di generare il report potresti voler forzare un salvataggio automatico
    alert("Generazione del report PDF in corso...");
    // window.open(`/sessions/${sessionId}/report`, '_blank');
  },

  // SBLOCCA NAVIGAZIONE (Usato dai link "+ Aggiungi Asset" e "Modifica")
  allowExit: () => {
    allowExit(); // Richiama la funzione interna per spegnere il lucchetto
  }
};

// 5. Inizializzazione quando il componente viene montato
onMounted(() => {
  // Esponiamo le funzioni all'oggetto window per farle "vedere" ai bottoni HTML di Jinja2
  window.dashboardAction = dashboardAction;

  // --- TRUCCO 1: ATTIVIAMO IL BLOCCO SCHEDA ---
  window.addEventListener('beforeunload', handleBeforeUnload);

  // --- TRUCCO 2: SUPER TRAPPOLA PER IL TASTO INDIETRO ---
  window.history.pushState({ locked: true }, "", window.location.href);
  window.history.pushState({ locked: true }, "", window.location.href);
  
  // Se l'utente preme il tasto indietro del browser, lo intercettiamo
  window.onpopstate = function (event) {
    // Rimettiamo subito lo stato fittizio per non farlo uscire
    window.history.pushState({ locked: true }, "", window.location.href);
    
    // Il tuo messaggio personalizzato!
    alert("Vuoi davvero uscire? Controlla di aver salvato e chiuso la sessione!");
  };

  console.log("Dashboard protetta avviata (Super-Lock attivo) per la sessione:", sessionId);
});

// Opzionale: pulizia se il componente Vue dovesse essere smontato
onUnmounted(() => {
  allowExit();
});
</script>