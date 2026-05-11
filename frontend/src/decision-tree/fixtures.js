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
