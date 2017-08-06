"""wattle : A module for implementing decision tree algorithms.

This module can be used to implement various decision tree algorithms. The
basic generic structure of decision tree algorithms is provided. Essentially,
all that is needed to do is add components such as splitting criteria and
pruning function.

"""

import copy

class Node:
  """A class for describing a decision tree node.

  Attributes:
    is_leaf (boolean): True if this node is a leaf. False otherwise.
    is_root (boolean): True if this node is the root. False otherwise.
    data_points (pandas.DataFrame): The data contained in this node.
    class_attribute (string): The name of the class attribute. e.g.:'Defective'
    class_supports (dict<int>): The number of data points for each class value.
      This is represented as a dictionary where each key is the name of the
      class value and each dictionary value is the number of records with that
      class value.
    parent (Node): The parent node of this node.
    children (List<Node>): A list of all this node's children.
    parent_branch (Branch): The branch connecting this node to its parent.
    child_branches (List<Branch>): A list containing the branches which connect
      this node to each of its children.
    """

    def __init__(self, data=None, class_attribute='', build=False,
      split_func=None, split_func_args, is_root=False, parent=None,
        parent_branch=None):
      """The Node constructor.

      Builds a Node object based on the arguments. Will build the node and then
      prune it if both build and prune are True. If prune is True but build is
      false, then no pruning will occur. Building and pruning are performed
      using the split_func and prune_func functions.

      Args:
        data (pandas.DataFrame): The data contained within this node.
        class_attribute (string): The name of the class attribute.
        build (boolean): Whether or not to build the node as part of the object
          construction process. This can be done manually later using the build
          function if desired.
        split_func (function): A function which takes a node as input and
          returns a Split_Test object which describes the best split for this
          node. The function should return None if there were no good splits
          found.
        split_func_args (list): A list of arguments to pass to the split
          function. They are passed in the order of the list.
        is_root (boolean): Whether or not this Node is a root of a tree.
        parent (Node): The parent node of this node.
        parent_branch (Branch): The parent branch of this node.
      """
      self.data_points = data
      self.class_attribute = class_attribute
      self.is_leaf = True
      self.is_root = False
      self.parent = None
      self.children = []
      self.child_branches = []
      class_supports = data[class_attribute].value_counts.to_dict()

      if not self.is_root:
        self.parent_branch = parent_branch
      else:
        self.parent_branch = None

      if build:
        self.split(split_func, split_func_args)

    def split(split_func, recursive=False, split_func_args=[]):
      """If a split can be found, the current node gets children from it.

      The children are also split if recursive is set to True.

      Args:
        split_func (function): A function which takes a node as input and
          returns a Split_Test object which describes the best split for this
          node. The function should return None if there were no good splits
          found.
        recursive (boolean): A flag which determines whether the resulting
          children should also be split.

      Returns:
        (boolean) : True if a split was performed, False otherwise.

      Raises:
        ValueError: If this node is not a leaf.
      """
      if not self.is_leaf:
        raise ValueError('Cannot split a node which is not a leaf.')

      # Find the best split based on the split function and create an empty
      # list of children which will be populated based on the split.
      test = split_func(node, *split_func_args)
      children = []
      
      # If there was no suitable test found:
      if test is None:
        return False

      # If the test attribute is categorical:
      if test.attribute_type = 'categorical':
        # The following solution to splitting based on a categorical attribute
        # was guided by the following stackoverflow answer by user
        # 'woody pride': https://goo.gl/uohhDi
        possible_values = self.data_points.loc(test.attribute_name).unique()
        data_splits = {elem : pd.DataFrame for elem in possible_values}
        for key in data_splits.keys():
          data_splits[key] = data[:][data.Names == key]

        # Create a new Node object for each resulting split.
        for split in data_splits.keys():
          data = data_splits[split]
          class_attribute = self.class_attribute

          # If the rescursive flag is set, create children which also split.
          child = None # Created below in the if-else block.
          if recursive:
            child = Node(data=data, parent=self,
              class_attribute=class_attribute, build=True,
              split_func=split_func, split_func_args=split_func_args)
          else:
            child = Node(data=data, parent=self,
              class_attribute=class_attribute)

          # Create a branch connecting the child to the parent.
          parent_branch = Branch(self, child, test)
          child.parent_branch = parent_branch
          children.append(child)

      # If the test attribute is numerical:
      elif test.attribute_type = 'numerical':

        # Get the data points for the left and right splits. Store the results
        # in a dictionary where the keys are 'left' and 'right'. These
        # represent the '<=' and '>' splits respectively.
        split_test = {}
        split_data = {}
        split_tests['left'] = data_points[test.attribute <= test.split_value]
        data_splits['left'] = self.data_points[split_tests['left']
        split_tests['right'] = data_points[test.attribute > test.split_value]
        data_splits['right'] = self.data_points[split_tests['right']]

        # Create the left and right children. If the recursive flag is set,
        # create children which also split.
        for split in data_splits.keys():
          data = data_splits[split]
          class_attribute = self.class_attribute

          # If the recursive flag is set, create children which also split.
          child = None # Created below in the if-else block.
          if recursive:
            child = Node(data=data, parent=self,
              class_attribute=class_attribute, build=True,
              split_func=split_func, split_func=split_func_args)
          else:
            child= Node(data=data, parent=self,
              class_attribute=class_attribute)
          
          # Create a branch connecting the child to the parent.
          if split = 'left':
            test.operator = '<='
          else:
            test.operator = '>'
          parent_branch = Branch(self, child, test)
          child.parent_branch = parent_branch
          children.append(child)

      # Finally, set the children of this Node to be the child nodes that were
      # created. This Node object is also no longer a leaf.
      self.children = children
      self.is_leaf = False
