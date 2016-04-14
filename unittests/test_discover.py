import os
import pitest
import unittest

class TestDiscover(unittest.TestCase):
    curr_dir = os.getcwd()
    this_dir = os.path.dirname(os.path.realpath(__file__))
    test_dir = os.path.join(curr_dir, 'test_dir')

    @classmethod
    def setUpClass(cls):
        os.chdir(cls.this_dir)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.curr_dir)

    def test_load_file(self):
        expected_names = {
            'test_dir.inter_file_deps.DemoCase8',
            'test_dir.inter_file_deps.DemoCase9',
            'test_dir.inter_file_deps.DemoCase10',
        }
        fname = os.path.join(self.test_dir, 'inter_file_deps.py')
        testcases = pitest.Discover.load_file(fname, baseclass = 'CaseBase1')
        actual_names = set([ name_obj.name for name_obj in testcases ])
        self.assertEqual(expected_names, actual_names)

    def test_load_file_basepath(self):
        expected_names = {
            'inter_file_deps.DemoCase8',
            'inter_file_deps.DemoCase9',
            'inter_file_deps.DemoCase10',
        }
        fname = os.path.join(self.test_dir, 'inter_file_deps.py')
        testcases = pitest.Discover.load_file(fname, baseclass = 'CaseBase1',
                basepath = self.test_dir)
        actual_names = set([ name_obj.name for name_obj in testcases ])
        self.assertEqual(expected_names, actual_names)

    def test_discover_single_file(self):
        expected_names = {
            'deps.DemoCase0',
            'deps.DemoCase1',
            'deps.DemoCase2',
            'deps.DemoCase3',
            'deps.DemoCase4',
        }
        testcases = pitest.Discover.discover(self.test_dir, pattern = 'deps.py',
                baseclass = 'CaseBase1', recursive = False)
        actual_names = set([ name_obj.name for name_obj in testcases ])
        self.assertEqual(expected_names, actual_names)

    def test_test_discover_glob(self):
        expected_names = {
            'deps.DemoCase0',
            'deps.DemoCase1',
            'deps.DemoCase2',
            'deps.DemoCase3',
            'deps.DemoCase4',
            'inter_file_deps.DemoCase8',
            'inter_file_deps.DemoCase9',
            'inter_file_deps.DemoCase10',
        }
        testcases = pitest.Discover.discover(self.test_dir, pattern = '*.py',
                baseclass = 'CaseBase1')
        actual_names = set([ name_obj.name for name_obj in testcases ])
        self.assertEqual(expected_names, actual_names)

if __name__ == '__main__':
    unittest.main(verbosity = 0)
