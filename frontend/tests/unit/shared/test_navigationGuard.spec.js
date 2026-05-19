// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { 
  enableNavigationGuard, 
  disableNavigationGuard, 
  temporarilyDisableNavigationGuard 
} from '../../../src/shared/navigationGuard.js';

// --- navigationGuard Shared Utility ------------------------------------------

describe('Utility condivisa navigationGuard', () => {
  
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers(); 
  });

  it('Dovrebbe abilitare la guardia aggiungendo l\'event listener beforeunload', () => {
    // "Spiamo" il metodo addEventListener di window senza sovrascriverlo del tutto
    const addListenerSpy = vi.spyOn(window, 'addEventListener');

    enableNavigationGuard();

    // 1. Verifica che il listener sia stato aggiunto all'evento giusto
    expect(addListenerSpy).toHaveBeenCalledTimes(1);
    expect(addListenerSpy).toHaveBeenCalledWith('beforeunload', expect.any(Function));

    // 2. Estraiamo la funzione interna (handleBeforeUnload) e la testiamo
    const handleBeforeUnload = addListenerSpy.mock.calls[0][1];
    
    // Creiamo un finto evento del browser
    const mockEvent = {
      preventDefault: vi.fn(),
      returnValue: undefined
    };

    // Eseguiamo la funzione interna passando il finto evento
    handleBeforeUnload(mockEvent);

    // Verifichiamo che blocchi l'uscita come previsto dalle API dei browser
    expect(mockEvent.preventDefault).toHaveBeenCalledTimes(1);
    expect(mockEvent.returnValue).toBe('');
  });

  it('Dovrebbe disabilitare la guardia rimuovendo l\'event listener beforeunload', () => {
    // "Spiamo" il metodo removeEventListener
    const removeListenerSpy = vi.spyOn(window, 'removeEventListener');

    disableNavigationGuard();

    expect(removeListenerSpy).toHaveBeenCalledTimes(1);
    expect(removeListenerSpy).toHaveBeenCalledWith('beforeunload', expect.any(Function));
  });

  it('Dovrebbe disabilitare temporaneamente la guardia e riabilitarla al termine del timeout', () => {
    // Attiviamo l'orologio fittizio di Vitest
    vi.useFakeTimers();
    
    const removeListenerSpy = vi.spyOn(window, 'removeEventListener');
    const addListenerSpy = vi.spyOn(window, 'addEventListener');

    // Chiamiamo la disabilitazione temporanea per 2000 millisecondi
    temporarilyDisableNavigationGuard(2000);

    // Subito dopo la chiamata, il listener deve essere stato RIMOSSO...
    expect(removeListenerSpy).toHaveBeenCalledTimes(1);
    // ...ma non deve ancora essere stato RIMESSO.
    expect(addListenerSpy).toHaveBeenCalledTimes(0);

    // avanziamo di 1999 millisecondi
    vi.advanceTimersByTime(1999);
    
    // A questo punto manca ancora 1 millisecondo, quindi la guardia non deve essersi riattivata
    expect(addListenerSpy).toHaveBeenCalledTimes(0);

    // Viaggiamo di un altro millisecondo (totale 2000)
    vi.advanceTimersByTime(1);
    
    // Il timeout è scattato, la guardia si è riattivata da sola!
    expect(addListenerSpy).toHaveBeenCalledTimes(1);
  });
});