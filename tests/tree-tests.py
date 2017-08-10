import sys
sys.path.append('../')
from src.wattle import Tree
import unittest

def cost_reduction_split(node, positive_class, cost_matrix):
  """Finds and returns the best split based on expected cost.

  Args:
    node (wattle.Node): The node to calculate the best split for.
    positive_class (string): The name of the class which is the positive class.
    cost_matrix (dict): The cost matrix represented like: {'TP':1,'TN':0} etc.

  Returns:
    (wattle.Split_Test): The best split based on expected cost.

  """

  # Calculate the expected cost of the parent.
  num_positive = node.num_positive(positive_class)
  num_negative = node.num_negative(positive_class)
  parent_cost = dc.expected_cost(num_positive, num_negative, cost_matrix)

  # These values will get updated if a better split is found.
  best_cost = float('inf')
  best_split = None

  # Iterate over every possible split.
  for split in node.get_possible_splits():

    # Get the class support counts for each resulting child.
    child_supports = node.get_split_supports(split, posneg=True,
      positive_class=positive_class)

    # If the cost of this split is better than the current best, update the
    # current best split to be this split.
    split_cost = dc.expected_cost_after_split(child_supports, cost_matrix)
    if split_cost < best_cost:
      best_cost = split_cost
      best_split = split
  
  if best_cost < parent_cost:
    return best_split
  else:
    return None

class test_tree_class(unittest.TestCase):
  def test_num_nodes(self):
    # Check that the number of nodes variable is correct.
    data = pd.read_csv('data/LOC_SDP.csv')
    cost_matrix = {'TP' : 1, 'TN' : 0, 'FP' : 1, 'FN' : 5}
    tree = Tree(data=data, build=True, split_func=cost_reduction_split,
      split_func_args=['1', cost_matrix])
    self.assertEqual(tree.num_nodes, 3)

  def test_find_node(self):
    # Checks that the correct node is found by the find_node function. If there
    # is no node that matches the passed logic rule, None should be returned.
    data = pd.read_csv('data/LOC_SDP.csv')
    cost_matrix = {'TP' : 1, 'TN' : 0, 'FP' : 1, 'FN' : 5}
    tree = Tree(data=data, build=True, split_func=cost_reduction_split,
      split_func_args=['1', cost_matrix])
    node = tree.find_node({'LOC' : '<= 73.5'})
    root_node = Node(data, class_attribute='Defective')
    root_node.split(cost_reduction_split, split_func_args=['1', cost_matrix])
    correct_node = root_node.children[0]
    self.assertEqual(node, root_node)

  def test_rules(self):
    # Checks that all rules are found from the tree as expected.
    correct_rules = []
    correct_rules.append('IF LOC <= 73.5 THEN {0 : 14, 1: 0}')
    correct_rules.append('IF LOC > 73.5 THEN {0 : 0, 1: 6}')
    data = pd.read_csv('data/LOC_SDP.csv')
    cost_matrix = {'TP' : 1, 'TN' : 0, 'FP' : 1, 'FN' : 5}
    tree = Tree(data=data, build=True, split_func=cost_reduction_split,
      split_func_args=['1', cost_matrix])
    self.assertEqual(set(correct_rules), set(tree.get_rules()))

  def test_string(self):
    # Check that the string representation is as expected.
    correct_string = 'LOC <= 73.5: {0 : 14, 1: 0}'
    correct_string += '\n'
    correct_string = 'LOC > 73.5: {0 : 0, 1: 6}'
    data = pd.read_csv('data/LOC_SDP.csv')
    cost_matrix = {'TP' : 1, 'TN' : 0, 'FP' : 1, 'FN' : 5}
    tree = Tree(data=data, build=True, split_func=cost_reduction_split,
      split_func_args=['1', cost_matrix])
    self.assertEqual(correct_string, str(tree))

if __name__ == '__main__':
    unittest.main(exit=False)
