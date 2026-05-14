/**
 * @typedef {'decision' | 'leaf'} NodeType
 * @typedef {'pass' | 'fail' | 'not_applicable'} EvaluationStateType
 */

/**
 * DecisionNode - un nodo con domanda e due figli (yes/no)
 */
export class DecisionNode {
  /** @param {{ id: string, question: string, parentId: string|null, yesChildId: string, noChildId: string }} opts */
  constructor({ id, question, parentId, yesChildId, noChildId }) {
    this.id = id;
    this.question = question;
    this.parentId = parentId;
    this.yesChildId = yesChildId;
    this.noChildId = noChildId;
  }

  /** @returns {{ id: string, type: NodeType, text: string, resultState: null, parentId: string|null, yesChildId: string, noChildId: string }} */
  getRenderData() {
    return {
      id: this.id,
      type: 'decision',
      text: this.question,
      resultState: null,
      parentId: this.parentId,
      yesChildId: this.yesChildId,
      noChildId: this.noChildId,
    };
  }

  /**
   * @param {boolean} answer
   * @returns {string|null}
   */
  getNext(answer) {
    return answer ? this.yesChildId : this.noChildId;
  }

  /** @returns {string|null} */
  getPrevious() {
    return this.parentId;
  }
}

/**
 * LeafNode - nodo terminale con verdetto
 */
export class LeafNode {
  /** @param {{ id: string, result: EvaluationStateType, parentId: string|null }} opts */
  constructor({ id, result, parentId }) {
    this.id = id;
    this.result = result;
    this.parentId = parentId;
  }

  /** @returns {{ id: string, type: NodeType, text: string, resultState: EvaluationStateType, parentId: string|null, yesChildId: null, noChildId: null }} */
  getRenderData() {
    return {
      id: this.id,
      type: 'leaf',
      text: this.result,
      resultState: this.result,
      parentId: this.parentId,
      yesChildId: null,
      noChildId: null,
    };
  }

  /**
   * @param {boolean} _answer
   * @returns {null}
   */
  getNext(_answer) {
    return null;
  }

  /** @returns {string|null} */
  getPrevious() {
    return this.parentId;
  }
}
