/**
 * Motore di valutazione: percorre l'albero secondo le risposte date
 * e produce il path attivo + i render data dei singoli nodi.
 */
export class EvaluationEngine {
  /** @type {import('./TreeStructure.js').TreeStructure} */
  #tree;

  /** @param {import('./TreeStructure.js').TreeStructure} tree */
  constructor(tree) {
    this.#tree = tree;
  }

  /**
   * Ritorna il DTO di rendering per un nodo.
   * @param {string} nodeId
   * @returns {Object|null}
   */
  getNodeRenderData(nodeId) {
    const node = this.#tree.getNode(nodeId);
    return node ? node.getRenderData() : null;
  }

  /**
   * Dato l'insieme delle risposte, calcola il percorso attivo dalla radice
   * fino alla foglia o fino al primo nodo senza risposta.
   * @param {Map<string, boolean>} answers
   * @returns {string[]}
   */
  getEvaluationPath(answers) {
    const path = [];
    let currentId = this.#tree.getRootId();

    while (currentId) {
      const node = this.#tree.getNode(currentId);
      if (!node) break;

      path.push(currentId);

      // Se è un leaf, ci fermiamo
      if (node.getNext === undefined || node.getRenderData().type === 'leaf') {
        break;
      }

      const answer = answers.get(currentId);
      if (answer === undefined) break; // nodo non ancora risposto

      currentId = node.getNext(answer);
    }

    return path;
  }

  /** @returns {import('./TreeStructure.js').TreeStructure} */
  getTree() {
    return this.#tree;
  }
}
