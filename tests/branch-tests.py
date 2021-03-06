import sys
sys.path.append('../')
from src.wattle import Branch, Node, Split_Test
import unittest

class test_branch_class(unittest.TestCase):
  def test_parent(self):
    # Check that the parent is correctly assigned.
    parent = Node(is_root=True)
    branch = Branch(parent=parent)
    self.assertEqual(branch.parent, parent)

  def test_child(self):
    # Check that the child is correctly assigned.
    child = Node(is_root=True)
    branch = Branch(child=child)
    self.assertEqual(branch.child, child)

  def test_string(self):
    # Check that the string representation is as expected.
    test = Split_Test(attribute_type='numerical', attribute='age',
      split_value=50, operator='>')
    branch = Branch(split_test=test)
    self.assertEqual(str(branch), 'age > 50')

if __name__ == '__main__':
    unittest.main(exit=False)
