// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach } from 'vitest';

// 1. Blocchiamo e simuliamo (mock) il file esterno che gestisce la navigazione.
vi.mock('@/shared/navigationGuard.js', () => ({
  enableNavigationGuard: vi.fn(),
  disableNavigationGuard: vi.fn(),
  temporarilyDisableNavigationGuard: vi.fn()
}));

// Importiamo le spie appena create per poter usare expect() su di esse
import { 
  enableNavigationGuard, 
  disableNavigationGuard, 
  temporarilyDisableNavigationGuard 
} from '@/shared/navigationGuard.js';

// --- Dashboard Main Entry ----------------------------------------------------

describe('Dashboard Main Entry (main.js)', () => {
  
  beforeEach(() => {
    vi.clearAllMocks();
    document.body.innerHTML = '';
    vi.resetModules();
  });

  it('abilita il blocco di navigazione al caricamento e collega correttamente i listener dei click', async () => {
    // creiamo finti bottoni/link con gli attributi dati
    const exitLink = document.createElement('a');
    exitLink.href = '#';
    exitLink.setAttribute('data-allow-exit', 'true');
    exitLink.textContent = 'Torna alla Home';
    document.body.appendChild(exitLink);

    const downloadLink = document.createElement('button');
    downloadLink.setAttribute('data-allow-download', 'true');
    downloadLink.textContent = 'Scarica Referto';
    document.body.appendChild(downloadLink);

    // 2. Importiamo dinamicamente il file main.js
    await import('../../../../src/widgets/dashboard/main.js');

    // Il file ha aggiunto il listener per 'load'. 
    window.dispatchEvent(new Event('load'));

    // Il blocco navigazione deve essere scattato subito dopo il load.
    expect(enableNavigationGuard).toHaveBeenCalledTimes(1);

    // Clicchiamo il finto link di uscita
    exitLink.click();
    expect(disableNavigationGuard).toHaveBeenCalledTimes(1);

    // Clicchiamo il finto bottone di esportazione
    downloadLink.click();
    expect(temporarilyDisableNavigationGuard).toHaveBeenCalledTimes(1);
    expect(temporarilyDisableNavigationGuard).toHaveBeenCalledWith(2000);
  });
});