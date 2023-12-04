import unittest
from chatgptupdate import to_singular

class TestToSingular(unittest.TestCase):
    def test_irregular_plurals(self):
        self.assertEqual(to_singular('feet'), 'foot')
        self.assertEqual(to_singular('teeth'), 'tooth')
        self.assertEqual(to_singular('geese'), 'goose')
        # Add more tests for irregular plurals

    def test_regular_ies_plurals(self):
        self.assertEqual(to_singular('batteries'), 'battery')
        self.assertEqual(to_singular('ponies'), 'pony')
        # Add more tests for words ending in 'ies'
    
    def test_regular_us_nonplurals(self):
        self.assertEqual(to_singular('plus'), 'plus')
    
    def test_regular_es_plurals(self):
        self.assertEqual(to_singular('boxes'), 'box')
        self.assertEqual(to_singular('bushes'), 'bush')
        # Add more tests for words ending in 'es'

    def test_regular_s_plurals(self):
        self.assertEqual(to_singular('cats'), 'cat')
        self.assertEqual(to_singular('dogs'), 'dog')
        # Add more tests for words ending in 's'

    def test_no_change(self):
        self.assertEqual(to_singular('child'), 'child')
        self.assertEqual(to_singular('sheep'), 'sheep')
        # Add more tests for words that should not



if __name__ == '__main__':
    unittest.main()