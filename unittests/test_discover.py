import os
import pitest
import unittest

class TestDiscover(unittest.TestCase):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    test_dir = os.path.join(curr_dir, 'test_dir')

    def test_load_single_file(self):
        expected_testcases = {'DemoCase8', 'DemoCase9', 'DemoCase10'}
        fname = os.path.join(self.test_dir, 'inter_file_deps.py')
        testcases = pitest.Discover.load_file(fname, baseclasses = ['CaseBase1'])
        actual_testcases = set([ x.__name__ for full_name, x in testcases ])
        self.assertEqual(actual_testcases, expected_testcases)

    def test_discover_single_file(self):
        expected_testcases = {'DemoCase0', 'DemoCase1', 'DemoCase2',
                'DemoCase3', 'DemoCase4'}
        testcases = pitest.Discover.discover(self.test_dir,
                baseclasses = ['CaseBase1'], pattern = 'deps.py')
        actual_testcases = set([ x.__name__ for full_name, x in testcases ])
        self.assertEqual(actual_testcases, expected_testcases)

    def test_test_discover_glob(self):
        expected_testcases = {'DemoCase0', 'DemoCase1', 'DemoCase2',
                'DemoCase3', 'DemoCase4', 'DemoCase8', 'DemoCase9',
                'DemoCase10'}
        testcases = pitest.Discover.discover(self.test_dir,
                baseclasses = ['CaseBase1'], pattern = '*.py')
        actual_testcases = set([ x.__name__ for full_name, x in testcases ])
        self.assertEqual(actual_testcases, expected_testcases)

class TestDiscoverInternals(unittest.TestCase):

    def test_convert_path(self):
        expect_true_samples = [
                ('path/to/unittest.py', 'path.to.unittest'),
                ('/path/to/unittest.py', '.path.to.unittest'),
                ('/path/to/unit-test.py', '.path.to.unit_test'),
                ('~/git/pylib.py', os.path.expanduser('~').replace('/',
                    '.').replace('-', '_') + '.git.pylib')
        ]
        expect_error_samples = [
                'usr/foo.bar', # does not end with '.py'
                'some.path/foo.bar', # has dot in the middle
        ]
        for fname, pname, in expect_true_samples:
            self.assertEqual(pitest.Discover._convert_path(fname), pname)
        for fname in expect_error_samples:
            with self.assertRaises(pitest.discover.DiscoverError):
                pitest.Discover._convert_path(fname)

    def test_match_full_class_name(self):
        expect_true_samples = [
                ('foo.bar.Case1', [ 'Case1' ]),
                ('foo.bar.Case1', [ 'Case1', 'foo.bar.Case2' ]),
                ('foo.bar.Case1', [ 'bar.Case1', 'Case2' ]),
        ]
        expect_false_samples = [
                ('foo.bar.Case1', [ 'foo.Case1' ]),
                ('foo.bar.Case1', [ 'foo.Case1', 'Case2' ]),
                ('foo.bar.Case100', [ 'foo.Case1', 'Case10' ]),
        ]
        for full_cls_name, baseclasses in expect_true_samples:
            self.assertTrue(pitest.Discover._match_full_class_name(full_cls_name, baseclasses))
        for full_cls_name, baseclasses in expect_false_samples:
            self.assertFalse(pitest.Discover._match_full_class_name(full_cls_name, baseclasses))

if __name__ == '__main__':
    unittest.main(verbosity = 0)
