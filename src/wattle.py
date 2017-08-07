"""wattle : A module for implementing decision tree algorithms.

This module can be used to implement various decision tree algorithms. The
basic generic structure of decision tree algorithms is provided. Essentially,
all that is needed to do is add components such as splitting criteria and
pruning function.

"""

import copy
import pandas as pd

class Node:
  """A class for describing a decision tree node.

  Attributes:
    is_leaf (boolean): True if this node is a leaf. False otherwise.
    is_root (boolean): True if this node is the root. False otherwise.
    data_points (pandas.DataFrame): The data contained in this node.
    class_attribute (string): The name of the class attribute. e.g.:'Defective'
    attribute_types (pandas.dtype): The type of each column in data_points.
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
          function. They are passed in the same order as this list.
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
      self.class_supports = data[class_attribute].value_counts.to_dict()

      if not self.is_root:
        self.parent_branch = parent_branch
      else:
        self.parent_branch = None

      if build:
        self.split(split_func, split_func_args)

      # Get the attribute types from the data.
      # The following solution was partly taken from: https://goo.gl/ARws3c
      attribute_types = []
      columns = data.columns
      numerical_columns = data._get_numeric_data().columns
      categorical_indexes = list(set(columns) - set(numerical_columns))
      for column in range(len(columns)):
        if column in categorical_indexes:
          self.attribute_types.append('categorical')
        else:
          self.attribute_types.append('numerical')

    def split(split_func, recursive=False, split_func_args=[]):
      """If a split can be found, the current node gets children from it.

      The children are also split if recursive is set to True.

      Args:
        split_func (function): A function which takes a node as input and
          returns a Split_Test object which describes the best split for this
          node. The function should return None if there were no good splits
          found.
        split_func_args (list): A list of arguments to pass to the split
          function. They are passed in the same order as this list.
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
      test = split_func(self, *split_func_args)
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

      # If a split was performed, return True and set the children of this Node
      # to be the child nodes that were created. This Node object is also no
      # longer a leaf. If a split wasn't performed, return False.
      if children:
        self.children = children
        self.is_leaf = False
        return True
      else:
        return False

    def prune(prune_func, prune_func_args):
      """Removes the children from this node if the prune function says so.
                                                                              
      Args:
        prune_func (function): A function which takes a node as input and
          returns True if the node should be pruned, and False otherwise.
        prune_func_args (list): A list of arguments to pass to the prune 
          function. They are passed in the same order as this list.
      Returns:
        (boolean) : True if a split was performed, False otherwise.
                                                                              
      Raises:
        ValueError: If any of this node's children are not leaves.
      """
      if not all(child.is_leaf for child in self.children):
        raise ValueError("Can't prune a node with a non-leaf child.")

      # If the prune function returns true, prune the node and return True.
      # Otherwise, return False.
      if prune_func(self, prune_func, *prune_func_args):
        self.children = []
        self.is_leaf = True
        self.child_branches = []
        return True
      else:
        return False

    def get_possible_splits():
      """Get the possible splits for this dataset. Returns them in a list.

      The list that is returned contains both categorical and numerical splits.

      Args: None

      Returns:
        (list<Split_Test>) : Split tests which can be used to split this node's
          data points.
      """
      # Define the list which will be appended to and returned.
      splits = []

      # It's cleaner to get the attribute names early.
      attribute_names = list(self.data_points)

      # For each index in the attribute list:
      for index in range(len(self.attribute_types)):
        if self.attribute_types[index] == 'categorical':
          splits.append(Split_Test('categorical', attribute_names[index]))
        elif self.attribute_types[index] == 'numerical':
          column = self.data_points[attribute_names[index]]
          unique_values = column.unique()

          # The following solution was taken from: https://goo.gl/8EyjgD
          a_values = unique_values[1:] # All values but first.
          b_values = unique_values[:-1] # All values but last.
          split_values = [(a + b) / 2 for a, b in zip(a_values, b_values)]

          for value in split_values:
            splits.append(Split_Test('numerical', attribute_names[index],
              value)

      # Finally, return the list of splits.
      return splits

    def get_split_supports(split_test):
      """Finds the supports for the children that would result from split_test.

      Args:
        split_test (Split_Test): Used to split the data.

      Returns:
        (List<Dict>): The i'th element in the list is the i'th class supports,
          where the class supports are represented in a dictionary. Each key in
          the dictionary is a class value. Each value is the support count for
          that value.
      """
      # Create a copy of this object and split it using split_test.
      temp_node = copy.deepcopy(self)
      temp_node.split({return split_test})

      # Add the support counts for each child to the return list.
      split_supports = []
      for child in temp_node.children:
        split_supports.append(child.class_supports)

      return split_supports
