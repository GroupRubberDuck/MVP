import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { EvaluationApiClient } from '../../../../src/widgets/requirement-evaluation/api/EvaluationApiClient.js';

// ─── EvaluationApiClient ────────────────────────────────────────

describe('EvaluationApiClient', () => {
  // Prepariamo dei finti URL iniettati (simulando il Livello 3)
  const mockUrls = {
    answer: '/api/eval/123/answer',
    state: '/api/eval/123/state',
    justification: '/api/eval/123/justification',
    detail: '/api/eval/123/detail',
  };

  let apiClient;

  beforeEach(() => {
    vi.clearAllMocks();
    // Intercettiamo la funzione globale fetch
    global.fetch = vi.fn();
    
    // Inizializziamo il client prima di ogni test
    apiClient = new EvaluationApiClient(mockUrls);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ─── saveAnswer ───

  it('SaveAnswer Chiama Fetch Con Put Body Corretto E Restituisce Il Json Parsato', async () => {
    const mockResponse = { success: true, updated: true };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await apiClient.saveAnswer({ nodeId: 'N1', answer: true });

    // Verifica configurazione della fetch
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(mockUrls.answer, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ node_id: 'N1', answer: true }),
    });

    // Verifica il ritorno
    expect(result).toEqual(mockResponse);
  });

  it('SaveAnswer Lancia Un Errore Se La Risposta Non È Ok', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
    });

    await expect(apiClient.saveAnswer({ nodeId: 'N1', answer: true }))
      .rejects.toThrow('saveAnswer failed: 400');
  });

  // ─── fetchState ───

  it('FetchState Chiama Fetch Con Get E Restituisce Il Json Parsato', async () => {
    const mockState = { status: 'in_progress', completed_nodes: [] };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockState),
    });

    const result = await apiClient.fetchState();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    // Fetch default method is GET, so no second argument is strictly required in the assertion
    expect(global.fetch).toHaveBeenCalledWith(mockUrls.state);
    
    expect(result).toEqual(mockState);
  });

  it('FetchState Lancia Un Errore Se La Risposta Non È Ok', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    await expect(apiClient.fetchState()).rejects.toThrow('fetchState failed: 404');
  });

  // ─── saveJustification ───

  it('SaveJustification Chiama Fetch Con Put Body Corretto E Restituisce Il Json Parsato', async () => {
    const mockResponse = { saved: true };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await apiClient.saveJustification({ justification: 'Non applicabile per motivi tecnici' });

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(mockUrls.justification, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ justification: 'Non applicabile per motivi tecnici' }),
    });

    expect(result).toEqual(mockResponse);
  });

  it('SaveJustification Lancia Un Errore Se La Risposta Non È Ok', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    await expect(apiClient.saveJustification({ justification: 'Test' }))
      .rejects.toThrow('saveJustification failed: 500');
  });

  // ─── fetchDetail ───

  it('FetchDetail Chiama Fetch Con Get E Restituisce Il Json Parsato', async () => {
    const mockDetail = { id: 123, nodes: [] };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockDetail),
    });

    const result = await apiClient.fetchDetail();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(mockUrls.detail);
    
    expect(result).toEqual(mockDetail);
  });

  it('FetchDetail Lancia Un Errore Se La Risposta Non È Ok', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 403,
    });

    await expect(apiClient.fetchDetail()).rejects.toThrow('fetchDetail failed: 403');
  });
});