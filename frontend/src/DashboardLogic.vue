<template>
  <!-- Componente invisibile che fa da "cervello" alla Dashboard -->
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';

const pathParts = window.location.pathname.split('/');
const sessionIndex = pathParts.indexOf('sessions');
const deviceIndex = pathParts.indexOf('devices');

const sessionId = sessionIndex !== -1 ? pathParts[sessionIndex + 1] : null;
const deviceId = deviceIndex !== -1 ? pathParts[deviceIndex + 1] : null; 

// 2. Gestione Blocco Navigazione
const handleBeforeUnload = (event) => {
  const message = "Valutazione in corso. Se esci ora, i dati non salvati andranno persi.";
  event.preventDefault();
  event.returnValue = message;
  return message;
};

const allowExit = () => {
  window.removeEventListener('beforeunload', handleBeforeUnload);
  window.onpopstate = null;
};

// 4. Azioni Dashboard
const dashboardAction = {
  // SALVA (PUT)
save: async () => {
    if (!sessionId) return alert("Errore: ID sessione non trovato.");
    

    
    try {
      // URL corretto con /commit e metodo POST allineato al controller
      const response = await fetch(`/sessions/${sessionId}/commit`, { method: 'POST' }); 
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Errore HTTP ${response.status}`);
      }
      
      alert("Sessione salvata con successo!");
    } catch (e) {
      alert("Impossibile salvare: " + e.message);
    }
  },

  close: async () => {
    if (!sessionId) return alert("Errore: ID sessione non trovato.");
    if (confirm("Sei sicuro di voler chiudere la sessione? I dati non salvati andranno persi.")) {
      try {
        const response = await fetch(`/sessions/${sessionId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error("Errore nella chiusura della sessione sul server.");
        allowExit(); 
        window.location.href = "/devices"; 
      } catch (e) {
        alert("Errore durante la chiusura: " + e.message);
      }
    }
  },

  // SALVA E CHIUDI
  saveAndClose: async () => {
    if (!sessionId) return alert("Errore: ID sessione non trovato.");
    
    try {
      // 1. Esegue il salvataggio
      const responseSave = await fetch(`/sessions/${sessionId}/commit`, { method: 'POST' }); 
      if (!responseSave.ok) {
        const errorData = await responseSave.json().catch(() => ({}));
        throw new Error(errorData.error || `Errore HTTP nel salvataggio ${responseSave.status}`);
      }
      
      // 2. Se il salvataggio va a buon fine, chiude direttamente senza chiedere conferma
      const responseClose = await fetch(`/sessions/${sessionId}`, { method: 'DELETE' });
      if (!responseClose.ok) {
        throw new Error("Dati salvati, ma errore nella chiusura della sessione sul server.");
      }
      
      // 3. Sblocca la navigazione ed esce
      allowExit(); 
      window.location.href = "/devices"; 
    } catch (e) {
      alert("Errore durante Salva e Chiudi: " + e.message);
    }
  },

  // GENERA REPORT 
  generateReport: () => {
    if (!sessionId || !deviceId) return alert("Errore: ID sessione o dispositivo mancanti.");

    // Disattiviamo temporaneamente il blocco per permettere al browser di gestire il file
    allowExit();
    console.log("Generazione report avviata...");

    // Avviamo il download con l'URL completo richiesto dal controller
    window.location.assign(`/sessions/${sessionId}/devices/${deviceId}/report/pdf`);

    setTimeout(() => {
      window.addEventListener('beforeunload', handleBeforeUnload);
    }, 1000);
  },
  
  allowExit: () => {
    allowExit(); 
  }
};

onMounted(() => {
  window.dashboardAction = dashboardAction;
  window.addEventListener('beforeunload', handleBeforeUnload);

  // Trappola tasto indietro
  window.history.pushState({ locked: true }, "", window.location.href);
  window.history.pushState({ locked: true }, "", window.location.href);
  
  window.onpopstate = function (event) {
    window.history.pushState({ locked: true }, "", window.location.href);
    alert("Vuoi davvero uscire? Controlla di aver salvato e chiuso la sessione!");
  };

  console.log("Dashboard protetta (ID Sessione:", sessionId, "| ID Dispositivo:", deviceId, ")");
});

onUnmounted(() => {
  allowExit();
});
</script>