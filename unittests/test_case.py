import os
import pitest
import unittest

class Case(pitest.TestCase):
    def test_foo():
        pass
    def test_bar():
        pass

class TestCase(unittest.TestCase):

    def test_get_method_names_class(self):
        expected = { 'test_foo', 'test_bar' }
        actual = Case._get_test_method_names_class()
        self.assertEqual(expected, set(actual))

    def test_get_method_by_name(self):
        samples_good = {
                'test_foo': 'test_foo',
                'test_case.test_foo': 'test_foo',
                't_case.test_foo': 'test_foo',
        }
        for fullname, method_name in samples_good.items():
            actual = Case()._get_method_by_name(fullname).__name__
            self.assertEqual(method_name, actual)

        samples_bad = [ 'fooo', 'test_cse.est_foo' ]
        for fullname in samples_bad:
            self.assertEqual(None, Case()._get_method_by_name(fullname))

if __name__ == '__main__':
    unittest.main(verbosity = 0)
