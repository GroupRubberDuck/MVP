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
   * @param {{ root_node_id: string, nodes: Array<Object> }} rawTree
   */
  constructor(rawTree) {
    this.#rootId = rawTree.root_node_id;

    // Prima passata: creiamo i nodi senza parentId
    const childToParent = new Map();

    for (const raw of rawTree.nodes) {
      if (raw.node_type === 'decision_node') {
        childToParent.set(raw.child_yes, raw.node_id);
        childToParent.set(raw.child_no, raw.node_id);
      }
    }

    // Seconda passata: creiamo le istanze con parentId risolti
    for (const raw of rawTree.nodes) {
      const parentId = childToParent.get(raw.node_id) ?? null;

      if (raw.node_type === 'decision_node') {
        this.#nodes.set(
          raw.node_id,
          new DecisionNode({
            id: raw.node_id,
            question: raw.question,
            parentId,
            yesChildId: raw.child_yes,
            noChildId: raw.child_no,
          })
        );
      } else if (raw.node_type === 'leaf_node') {
        this.#nodes.set(
          raw.node_id,
          new LeafNode({
            id: raw.node_id,
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
