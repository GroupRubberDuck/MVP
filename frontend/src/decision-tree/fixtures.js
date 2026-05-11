export const sampleTree = {
  root_node_id: 'N1',
  nodes: [
    {
      node_id: 'N1',
      node_type: 'decision_node',
      question: 'Is the public accessibility of the equipment\'s intended equipment functionality?',
      child_yes: 'N2',
      child_no: 'L1',
    },
    {
      node_id: 'N2',
      node_type: 'decision_node',
      question: 'Do the physical or logical measures in the targeted operational environment limit the accessibility to authorized entities?',
      child_yes: 'L1',
      child_no: 'N3',
    },
    {
      node_id: 'N3',
      node_type: 'decision_node',
      question: 'Do legal implications not allow access control mechanisms?',
      child_yes: 'L2',
      child_no: 'N4',
    },
    {
      node_id: 'N4',
      node_type: 'decision_node',
      question: 'Are there access control mechanisms that manage entities\' access to the security asset and network asset?',
      child_yes: 'L1',
      child_no: 'L3',
    },
    { node_id: 'L1', node_type: 'leaf_node', verdict: 'pass' },
    { node_id: 'L2', node_type: 'leaf_node', verdict: 'not_applicable' },
    { node_id: 'L3', node_type: 'leaf_node', verdict: 'fail' },
  ],
};

/**
 * Stesso albero nel formato che arriva dal backend Flask (DecisionTreeDTO).
 * nodes è una mappa {nodeId: nodeDTO}, node_type è "decision"/"leaf",
 * i campi usano yes_child_id / no_child_id / parent_id.
 */
export const sampleTreeBackendFormat = {
  root_node_id: 'N1',
  nodes: {
    N1: {
      node_type: 'decision',
      question: 'Is the public accessibility of the equipment\'s intended equipment functionality?',
      parent_id: null,
      yes_child_id: 'N2',
      no_child_id: 'L1',
    },
    N2: {
      node_type: 'decision',
      question: 'Do the physical or logical measures limit accessibility?',
      parent_id: 'N1',
      yes_child_id: 'L1',
      no_child_id: 'N3',
    },
    N3: {
      node_type: 'decision',
      question: 'Do legal implications not allow access control mechanisms?',
      parent_id: 'N2',
      yes_child_id: 'L2',
      no_child_id: 'N4',
    },
    N4: {
      node_type: 'decision',
      question: 'Are there access control mechanisms?',
      parent_id: 'N3',
      yes_child_id: 'L1',
      no_child_id: 'L3',
    },
    L1: { node_type: 'leaf', parent_id: 'N1', verdict: 'pass' },
    L2: { node_type: 'leaf', parent_id: 'N3', verdict: 'not_applicable' },
    L3: { node_type: 'leaf', parent_id: 'N4', verdict: 'fail' },
  },
};
