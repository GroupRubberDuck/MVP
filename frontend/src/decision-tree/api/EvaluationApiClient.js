/**
 * Client API per persistere le risposte e recuperare lo stato di valutazione.
 */
export class EvaluationApiClient {
  /** @type {string} */
  #baseUrl;

  /** @param {string} baseUrl */
  constructor(baseUrl) {
    this.#baseUrl = baseUrl.replace(/\/$/, '');
  }

  /**
   * Salva una risposta singola.
   * @param {{ answer: boolean, deviceId: string, assetId: string, requirementId: string, nodeId: string }} params
   * @returns {Promise<Object>}
   */
  async saveAnswer({ answer, deviceId, assetId, requirementId, nodeId }) {
    const res = await fetch(`${this.#baseUrl}/answers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        answer,
        device_id: deviceId,
        asset_id: assetId,
        requirement_id: requirementId,
        node_id: nodeId,
      }),
    });

    if (!res.ok) throw new Error(`API saveAnswer failed: ${res.status}`);
    return res.json();
  }

  /**
   * Recupera lo stato di valutazione corrente per un requisito.
   * @param {{ deviceId: string, assetId: string, requirementId: string }} params
   * @returns {Promise<Object>}
   */
  async fetchRequirementEvaluationState({ deviceId, assetId, requirementId }) {
    const params = new URLSearchParams({
      device_id: deviceId,
      asset_id: assetId,
      requirement_id: requirementId,
    });

    const res = await fetch(`${this.#baseUrl}/evaluation-state?${params}`);
    if (!res.ok) throw new Error(`API fetchEvaluationState failed: ${res.status}`);
    return res.json();
  }
}
