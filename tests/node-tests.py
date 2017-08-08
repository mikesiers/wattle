import sys
import unittest
import pandas as pd
import datacost as dc
sys.path.append('../')
from src.wattle import Node

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
    temp_node = node # This temp node gets split.
    child_support_dicts = temp_node.get_split_supports(lambda: split)
    child_supports = [list(x.values()) for x in child_support_dicts]

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

class test_node_class(unittest.TestCase):
  def test_split_made(self):
    # Check that a split is made as and when expected.
    data = pd.read_csv('data/LOC_SDP.csv')
    node = Node(data, class_attribute='Defective')
    cost_matrix = {'TP' : 1, 'TN' : 0, 'FP' : 1, 'FN' : 5}
    node.split(cost_reduction_split(node, '1', cost_matrix))
    for branch in child_branch:
      assertEqual(branch.Split_Test.split_value, 73.5)

  def test_split_not_made(self):
    # Check that a split isn't made when not expected.
    node = Node()
    node.is_leaf = True
    node.split(lambda _: False)
    self.assertTrue(node.is_leaf)
    
  def test_split_return(self):
    # Check that the correct value is returned from the split function.
    node = Node()
    self.assertTrue(node.split(lambda _: True))

  def test_prune(self):
    # Check that the node is pruned when expected.
    node = Node()
    node.children = [Node(), Node()]
    node.is_leaf = False
    node.prune(lambda _: True)
    self.assertTrue(node.is_leaf)

  def test_prune_return(self):
    # Check that the correct value is returned from the prune function.
    node = Node()
    node.children = [Node(), Node()]
    node.is_leaf = False
    self.assertTrue(node.prune(lambda _: True))
    self.assertFalse(node.prune(lambda _: False))

  def test_string(self):
    # Check that the string representation is as expected.
    node = Node()
    node.class_supports = {'Y' : 35, 'N' : 11}
    expected_string = '{Y : 35, N : 11}'
    self.assertEqual(str(node), expected_string)

if __name__ == '__main__':
    unittest.main(exit=False)
