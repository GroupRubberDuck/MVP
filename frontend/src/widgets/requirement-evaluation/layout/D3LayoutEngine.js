import * as d3 from 'd3';

/**
 * @typedef {{ id: string, type: string, text: string, resultState: string|null, x: number, y: number }} NodeDTO
 * @typedef {{ id: string, sourceId: string, targetId: string, startX: number, startY: number, endX: number, endY: number, label: string }} EdgeDTO
 * @typedef {{ nodes: NodeDTO[], edges: EdgeDTO[] }} LayoutResult
 */

/**
 * Motore di layout basato su d3.tree().
 * Converte la mappa piatta di nodi in una struttura gerarchica per d3,
 * poi estrae posizioni assolute per nodi e archi.
 */
export class D3LayoutEngine {
  /** @type {{ width: number, height: number, nodeWidth: number, nodeHeight: number }} */
  #config;

  /**
   * @param {{ width?: number, height?: number, nodeWidth?: number, nodeHeight?: number }} [config]
   */
  constructor(config = {}) {
    this.#config = {
      width: config.width ?? 900,
      height: config.height ?? 500,
      nodeWidth: config.nodeWidth ?? 220,
      nodeHeight: config.nodeHeight ?? 140,
    };
  }

  /**
   * @param {Map<string, import('../models/Node.js').DecisionNode|import('../models/Node.js').LeafNode>} treeMap
   * @param {string} rootId
   * @returns {LayoutResult}
   */
  calculateLayout(treeMap, rootId) {
    const hierarchyData = this.#buildHierarchy(treeMap, rootId);
    const root = d3.hierarchy(hierarchyData);

    const treeLayout = d3.tree().nodeSize([
      this.#config.nodeWidth + 40,
      this.#config.nodeHeight + 40,
    ]);

    treeLayout(root);

    const nodes = this.#extractNodes(root);
    const edges = this.#extractEdges(root);

    return { nodes, edges };
  }

  /**
   * Costruisce la gerarchia ricorsiva per d3.hierarchy()
   * @param {Map} treeMap
   * @param {string} nodeId
   * @returns {Object}
   */
  #buildHierarchy(treeMap, nodeId) {
    const node = treeMap.get(nodeId);
    if (!node) return null;

    const data = node.getRenderData();
    const result = { ...data, children: [] };

    if (data.type === 'decision') {
      // Ordine: yes a sinistra, no a destra
      if (data.yesChildId) {
        const yesChild = this.#buildHierarchy(treeMap, data.yesChildId);
        if (yesChild) {
          yesChild._edgeLabel = 'Yes';
          result.children.push(yesChild);
        }
      }
      if (data.noChildId) {
        const noChild = this.#buildHierarchy(treeMap, data.noChildId);
        if (noChild) {
          noChild._edgeLabel = 'No';
          result.children.push(noChild);
        }
      }
    }

    if (result.children.length === 0) delete result.children;

    return result;
  }

  /**
   * @param {d3.HierarchyPointNode} root
   * @returns {NodeDTO[]}
   */
  #extractNodes(root) {
    return root.descendants().map((d) => ({
      id: d.data.id,
      type: d.data.type,
      text: d.data.text,
      resultState: d.data.resultState,
      x: d.x,
      y: d.y,
    }));
  }

  /**
   * @param {d3.HierarchyPointNode} root
   * @returns {EdgeDTO[]}
   */
  #extractEdges(root) {
    return root.links().map((link) => ({
      id: `${link.source.data.id}->${link.target.data.id}`,
      sourceId: link.source.data.id,
      targetId: link.target.data.id,
      startX: link.source.x,
      startY: link.source.y,
      endX: link.target.x,
      endY: link.target.y,
      label: link.target.data._edgeLabel ?? '',
    }));
  }
}
