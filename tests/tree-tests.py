import sys
sys.path.append('../')
#from src.wattle import Tree
import unittest

class test_tree_class(unittest.TestCase):
  def test_num_nodes(self):
    # Check that the number of nodes variable is correct.
    pass
  def test_build(self):
    # Check that the tree is built as expected. This will include the num_nodes
    # variable being updated.
    pass
  def test_find_node(self):
    # Checks that the correct node is found by the find_node function. If there
    # is no node that matches the passed logic rule, None should be returned.
    pass
  def test_rules(self):
    # Checks that all rules are found from the tree as expected.
    pass
  def test_string(self):
    # Check that the string representation is as expected.
    pass

if __name__ == '__main__':
    unittest.main(exit=False)
