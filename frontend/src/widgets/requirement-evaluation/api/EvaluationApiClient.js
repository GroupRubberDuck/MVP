// api/EvaluationApiClient.js
//
// Client API per la valutazione dei requisiti.
// Riceve URL pronti dal Livello 3 — non costruisce path.
//
// Responsabilità (SRP):
//   - Eseguire le chiamate HTTP verso gli endpoint di valutazione
//   - Parsare le risposte e lanciare errori in caso di fallimento
//
// NON è responsabile di:
//   - Conoscere la struttura delle rotte (URL iniettati dall'esterno)
//   - Gestire stato UI (delegato allo store/componenti)

export class EvaluationApiClient {
  #urls

  /**
   * @param {{ answer: string, justification: string, detail: string }} urls
   */
  constructor(urls) {
    this.#urls = urls
  }

  /**
   * Salva una risposta a un nodo dell'albero decisionale.
   * @param {{ nodeId: string, answer: boolean }} params
   */
  async saveAnswer({ nodeId, answer }) {
    const res = await fetch(this.#urls.answer, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        node_id: nodeId,
        answer,
      }),
    })

    if (!res.ok) throw new Error(`saveAnswer failed: ${res.status}`)
    return res.json()
  }

  
async fetchState() {
  const res = await fetch(this.#urls.state)
  if (!res.ok) throw new Error(`fetchState failed: ${res.status}`)
  return res.json()
}
  /**
   * Salva la giustificazione per il requisito.
   * @param {{ justification: string }} params
   */
  async saveJustification({ justification }) {
    const res = await fetch(this.#urls.justification, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ justification }),
    })

    if (!res.ok) throw new Error(`saveJustification failed: ${res.status}`)
    return res.json()
  }

  /**
   * Recupera il dettaglio aggiornato della valutazione.
   */
  async fetchDetail() {
    const res = await fetch(this.#urls.detail)
    if (!res.ok) throw new Error(`fetchDetail failed: ${res.status}`)
    return res.json()
  }
}