import { DecisionNode, LeafNode } from './Node.js';

/**
 * Rappresentazione piatta dell'albero per lookup rapido.
 * Costruisce DecisionNode/LeafNode dal JSON grezzo e calcola i parentId.
 */
export class TreeStructure {
  /** @type {Map<string, DecisionNode|LeafNode>} */
  #nodes = new Map();
  /** @type {string} */
  #rootId;

  /**
   * Accetta due formati:
   *  - Array (JSON iniziale): { root_node_id, nodes: [{ node_id, node_type, ... }] }
   *  - Mappa (backend DTO):   { root_node_id, nodes: { "N1": { node_type, parent_id, ... }, ... } }
   *
   * @param {{ root_node_id: string, nodes: Array<Object>|Record<string, Object> }} rawTree
   */
  constructor(rawTree) {
    this.#rootId = rawTree.root_node_id;

    // Normalizza: se è una mappa la convertiamo in entries [id, rawNode]
    const entries = Array.isArray(rawTree.nodes)
      ? rawTree.nodes.map((n) => [n.node_id, n])
      : Object.entries(rawTree.nodes);

    // Prima passata: calcola parentId per il formato array (il formato mappa li ha già)
    const isArrayFormat = Array.isArray(rawTree.nodes);
    const childToParent = new Map();

    if (isArrayFormat) {
      for (const [, raw] of entries) {
        if (raw.node_type === 'decision_node') {
          childToParent.set(raw.child_yes, raw.node_id);
          childToParent.set(raw.child_no, raw.node_id);
        }
      }
    }

    // Seconda passata: costruisci le istanze
    for (const [nodeId, raw] of entries) {
      const nodeType = raw.node_type;
      // Risolvi parentId: il backend lo passa come parent_id, l'array lo calcola
      const parentId = raw.parent_id ?? childToParent.get(nodeId) ?? null;

      if (nodeType === 'decision_node' || nodeType === 'decision') {
        this.#nodes.set(
          nodeId,
          new DecisionNode({
            id: nodeId,
            question: raw.question,
            parentId,
            // Supporta entrambe le naming convention
            yesChildId: raw.child_yes ?? raw.yes_child_id,
            noChildId: raw.child_no ?? raw.no_child_id,
          })
        );
      } else if (nodeType === 'leaf_node' || nodeType === 'leaf') {
        this.#nodes.set(
          nodeId,
          new LeafNode({
            id: nodeId,
            result: raw.verdict,
            parentId,
          })
        );
      }
    }
  }

  /** @param {string} id @returns {DecisionNode|LeafNode|null} */
  getNode(id) {
    return this.#nodes.get(id) ?? null;
  }

  /** @returns {string} */
  getRootId() {
    return this.#rootId;
  }

  /** @returns {Map<string, DecisionNode|LeafNode>} */
  getAllNodes() {
    return this.#nodes;
  }
}
