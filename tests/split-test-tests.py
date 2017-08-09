import sys
import unittest
sys.path.append('../')
from src.wattle import Split_Test

class test_split_test_class(unittest.TestCase):
  def test_is_numerical(self):
    # Check that is_numerical outputs the expected answer.
    test = Split_Test(attribute_type='numerical')
    self.assertTrue(test.is_numerical())
    test = Split_Test(attribute_type='categorical')
    self.assertFalse(test.is_numerical())

  def test_is_categorical(self):
    # Check that is_categorical outputs the expected answer.
    test = Split_Test(attribute_type='categorical')
    self.assertTrue(test.is_categorical())
    test = Split_Test(attribute_type='numerical')
    self.assertFalse(test.is_categorical())

  def test_string(self):
    # Check that the string representation is as expected.
    test = Split_Test(attribute='age', attribute_type='numerical',
      split_value=55.0, operator='>')
    assertEqual(test, 'age > 55.0')
    test = Split_Test(attribute='colour', attribute_type='categorical',
      split_value='red')
    assertEqual(test, 'colour = red')

if __name__ == '__main__':
    unittest.main(exit=False)
