"""wattle : A module for implementing decision tree algorithms.

This module can be used to implement various decision tree algorithms. The
basic generic structure of decision tree algorithms is provided. Essentially,
all that is needed to do is add components such as splitting criteria and
pruning function.

"""

import copy
import pandas as pd
import numpy as np
import datacost as dc

class Split_Test:
  """A class for describing a decision tree split test.

  Attributes:
    attribute_type (str): Either 'numerical' or 'categorical'.
    attribute (str): The name of the attribute to test.
    split_value (float OR string): If attribute_type='numerical', it is a
      float. If it is 'categorical' then it is a string.
    operator (str): Can be '<=' or '>'. For example, if the operator is '>'
      then the test will be 'if attribute > split_value. This value is only
      used when attribute_type = 'numerical'.
  """
  def __init__(self, attribute_type=None, attribute=None, split_value=None,
    operator=None):
    """The Split_Test constructor.

    The values of the resulting Split_Test object are set as the arguments.
    However, the operator value is set manually outside the constructor. The
    choice to do this was made because operator is not set until later in the
    wattle tree building process.

    Args:
      attribute_type (str): Either 'numerical' or 'categorical'.
      attribute (str): The name of the attribute to test.
      split_value (float OR string): A float or string which is the splitting
        point. If attribute_type='numerical', it is a float. If it is
        'categorical' then it is a string.
      operator (str): Can be '<=' or '>'. For example, if the operator is '>'
        then the test will be 'if attribute > split_value. This value is only
        used when attribute_type = 'numerical'.
    """
    self.attribute_type = attribute_type
    self.attribute = attribute
    self.split_value = split_value
    self.operator = operator

  def is_numerical(self):
    """Returns whether or not the Split_Test attribute is numerical.

    Returns:
      (boolean): True if attribute_type == 'numerical'. False otherwise.
    """
    return(self.attribute_type == 'numerical')

  def is_categorical(self):
    """Returns whether or not the Split_Test attribute is categorical.
                                                                         
    Returns:
      (boolean): True if attribute_type == 'categorical'. False otherwise.
    """
    return(self.attribute_type == 'categorical')

  def __str__(self):
    """The string representation for this object.
                                                                           
    The representation is in the form 'attribute operator split value'.
                                                                           
    Returns:
      (string): This node object represented as a string.
    """
    return self.attribute + self.operator + str(self.split_value)

  def __eq__(self, other):
    """Split_Test equality function.
                                                                        
    Args:
      other (Node): The Split_Test object to check equality for.
                                                                        
    Returns:
      (boolean): True if self and other are equal. False otherwise.
    """
    if self.attribute_type != other.attribute_type or\
      self.attribute != other.attribute or\
      self.split_value != other.split_value or\
      self.operator != other.operator:
      return False
    else:
      return True
                                                                        
  def __ne__(self, other):
    """Split_Test inequality function.
                                                                        
    Args:
      other (Node): The Split_Test object to check inequality for.
                                                                        
    Returns:
      (boolean): True if self and other are not equal. False otherwise.
    """
    return not __eq__(other)

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
  def __init__(self, data=None, class_attribute=None, build=False,
    split_func=None, split_func_args=[], is_root=False, parent=None,
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

    # If the class attribute and data were provided, calculate the class
    # supports. Since the class values may be non-string types, convert them to
    # strings.
    if data is not None and class_attribute is not None:
      self.class_supports = data[class_attribute].value_counts().to_dict()
      self.class_supports = {str(k):v for k,v in self.class_supports.items()}
    else:
      self.class_supports = {}

    # Set the parent branch if this node is not a root node.
    if not self.is_root:
      self.parent_branch = parent_branch
    else:
      self.parent_branch = None

    # Split the node if the build flag was set.
    if build:
      self.split(split_func, split_func_args)

    # Get the attribute types from the data.
    # The following solution was partly taken from: https://goo.gl/ARws3c
    # Only perform this if data was provided to the constructor:
    self.attribute_types = []
    if data is not None:
      columns = data.columns
      numerical_columns = data._get_numeric_data().columns
      categorical_indexes = list(set(columns) - set(numerical_columns))
      for column in range(len(columns)):
        if column in categorical_indexes:
          self.attribute_types.append('categorical')
        else:
          self.attribute_types.append('numerical')

  def split(self, split_func, recursive=False, split_func_args=[]):
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
    if test.attribute_type == 'categorical':
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
    elif test.attribute_type == 'numerical':

      # Get the data points for the left and right splits. Store the results
      # in a dictionary where the keys are 'left' and 'right'. These
      # represent the '<=' and '>' splits respectively.
      split_tests = {}
      data_splits = {}
      split_tests['left'] = data_points[test.attribute <= test.split_value]
      data_splits['left'] = self.data_points[split_tests['left']]
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
            split_func=split_func, split_func_args=split_func_args)
        else:
          child= Node(data=data, parent=self,
            class_attribute=class_attribute)
        
        # Create a branch connecting the child to the parent.
        if split == 'left':
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

  def prune(self, prune_func=None, prune_func_args=[]):
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
    if prune_func(self, *prune_func_args):
      self.children = []
      self.is_leaf = True
      self.child_branches = []
      return True
    else:
      return False

  def get_possible_splits(self):
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
            value))

    # Finally, return the list of splits.
    return splits

  def get_split_supports(self, split_test):
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
    temp_node.split(lambda: split_test)

    # Add the support counts for each child to the return list.
    split_supports = []
    for child in temp_node.children:
      split_supports.append(child.class_supports)

    return split_supports

  def num_records(self):
    """Gets the number of records in this Node object.

    Returns:
      (int): The number of records in this Node object. (len(data_points)).
    """
    return len(self.data_points)

  def num_positive(self, positive_class):
    """Gets the number of positive data points in this node.

    This is a trivial operation. However, it is provided so that the number
    of negative data points and positive data points are found in the same
    way.

    Args:
      positive_class (string): The postivie class value.

    Returns:
      (int): The number of positive records in this node.
    """
    return self.class_supports[positive_class]

  def num_negative(self, positive_class):
    """Gets the number of negative data points in this node.
                                                                            
    Args:
      positive_class (string): The postivie class value.
                                                                              
    Returns:
      (int): The number of negative records in this node.
    """
    supports = self.class_supports
    return np.sum(value for key, value in supports.items()\
      if key != positive_class)

  def num_errors(self, cost_sensitive=False, cost_matrix={},
    positive_class=''):
    """Finds the number of resubstitution errors for this node.

    The number of resubstitution errors is described as follows: If the data
    points contained within this node were classified using this node, how
    many errors would there be?

    Args:
      cost_sensitive (boolean): Whether or not to determine the label of this
        node cost-sensitively or not. For example, if this is False, the
        class value with the highest support is used as the label. If true,
        the class value with the lowest total cost is used as the label. If
        this is True, a cost matrix must also be provided.
      cost_matrix (dict<float>): This is used if the cost_sensitive flag is
        set to True. It is used to calculate the label with the lowest total
        cost. It is a dictionary which includes the keys: 'TP', 'TN', 'FP',
        and 'FN'. The values for this dictionary are the costs associated
        with the corresponding key. For example, 'TP' : 10 means that a true
        positive prediction has an associated cost of 10.
      positive_class (string): The positive class value.

    Returns:
      (int): The number of resubsitution errors for this node.

    Raises:
      ValueError: If cost_matrix is missing one of the following keys: TP, TN
        FP, FN. This will only be raised if the cost_sensitive flag is True.
    """
    # Get the class supports (so that the following code is cleaner)
    supports = self.class_supports
    label = '' # The label for that this node uses to classify records.
    num_errors = -1 # The value that will be returned.

    if cost_sensitive:
      if any(k not in cost_matrix for k in ('TP', 'TN', 'FP', 'FN')):
        raise ValueError('A cost is missing from the passed cost matrix.')

      # Get the number of positive and negative data points.
      num_positive = self.num_positive(positive_class)
      num_negative = self.num_negative(positive_class)

      # Using the number of positive and negative data points, find out
      # whether it is cheapest to label the records in this node object as
      # positive or negative.
      cost_positive = dc.cost_labelling_positive(num_positive, num_negative,
        cost_matrix)
      cost_negative = dc.cost_labelling_negative(num_positive, num_negative,
        cost_matrix)
      if cost_positive <= cost_negative:
        num_errors = num_negative
      else:
        num_errors = num_positive
        
    else:
      # The records are labelled as the majority class of this node.
      label = max(supports, key=lambda key: supports[key])
      num_errors = np.sum(value for key, value in supports.iteritems()\
        if key != label)

    return num_errors

  def __str__(self):
    """The string representation for this object.

    The representation is simply the class supports in a JSON-like format.

    Returns:
      (string): This node object represented as a string.
    """
    # The following solution is taken from: https://goo.gl/jU6xJ4
    supports = self.class_supports
    string = '{'
    for value, support in supports.items():
      string += str(value) + ' : ' + str(support) + ', '
    string = string[:-2]
    string += '}'
    return(string)

  def __eq__(self, other):
    """Node equality function.

    Args:
      other (Node): The node object to check equality for.

    Returns:
      (boolean): True if self and other are equal. False otherwise.
    """
    if self.is_leaf != other.is_leaf or\
      self.is_root != other.is_root or\
      self.class_attribute != other.class_attribute or\
      self.parent != other.parent or\
      self.children != other.children or\
      self.parent_branch != other.parent_branch or\
      self.child_branches != other.child_branches:
      return False
    else:
      return True

  def __ne__(self, other):
    """Node inequality function.

    Args:
      other (Node): The node object to check inequality for.

    Returns:
      (boolean): True if self and other are not equal. False otherwise.
    """
    return not __eq__(other)
