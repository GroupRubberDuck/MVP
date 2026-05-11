/**
 * Client API allineato alle route Flask del backend.
 *
 * Base URL atteso: la radice del blueprint (es. "/api/evaluation")
 * Le route reali seguono il pattern:
 *   /sessions/{sessionId}/devices/{deviceId}/assets/{assetId}/requirements/{requirementId}
 *   /sessions/{sessionId}/assets/{assetId}/requirements/{requirementId}/justification
 */
export class EvaluationApiClient {
  /** @type {string} */
  #baseUrl;

  /** @param {string} baseUrl */
  constructor(baseUrl) {
    this.#baseUrl = baseUrl.replace(/\/$/, '');
  }

  /**
   * Costruisce il path base per un requisito specifico.
   * @param {{ sessionId: string, deviceId: string, assetId: string, requirementId: string }} ctx
   */
  #requirementPath({ sessionId, deviceId, assetId, requirementId }) {
    return `${this.#baseUrl}/sessions/${sessionId}/devices/${deviceId}/assets/${assetId}/requirements/${requirementId}`;
  }

  /**
   * Recupera il dettaglio della valutazione (albero + risposte + stato).
   * GET /sessions/:sid/devices/:did/assets/:aid/requirements/:rid
   * @param {{ sessionId: string, deviceId: string, assetId: string, requirementId: string }} ctx
   * @returns {Promise<Object>} RequirementEvaluationDTO serializzato
   */
  async fetchRequirementEvaluationDetail(ctx) {
    const res = await fetch(this.#requirementPath(ctx));
    if (!res.ok) throw new Error(`fetchRequirementEvaluationDetail failed: ${res.status}`);
    return res.json();
  }

  /**
   * Salva una risposta a un nodo dell'albero decisionale.
   * POST /sessions/:sid/devices/:did/assets/:aid/requirements/:rid/answer
   * @param {{ sessionId: string, deviceId: string, assetId: string, requirementId: string, nodeId: string, answer: boolean }} params
   * @returns {Promise<Object>}
   */
  async saveAnswer({ sessionId, deviceId, assetId, requirementId, nodeId, answer }) {
    const res = await fetch(`${this.#requirementPath({ sessionId, deviceId, assetId, requirementId })}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        node_id: nodeId,
        answer,
      }),
    });

    if (!res.ok) throw new Error(`saveAnswer failed: ${res.status}`);
    return res.json();
  }

  /**
   * Inserisce o aggiorna la giustificazione per un requisito.
   * PUT /sessions/:sid/assets/:aid/requirements/:rid/justification
   * Nota: questa route NON ha deviceId nel path (come da controller Flask).
   * @param {{ sessionId: string, assetId: string, requirementId: string, justification: string }} params
   * @returns {Promise<Object>}
   */
  async saveJustification({ sessionId, assetId, requirementId, justification }) {
    const res = await fetch(
      `${this.#baseUrl}/sessions/${sessionId}/assets/${assetId}/requirements/${requirementId}/justification`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ justification }),
      }
    );

    if (!res.ok) throw new Error(`saveJustification failed: ${res.status}`);
    return res.json();
  }
}
