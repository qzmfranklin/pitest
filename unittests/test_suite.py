import os
import pitest
import unittest

class TestSuiteDemo1(pitest.TestSuiteBase):
    testcase_baseclasses = [ 'CaseBase1' ]

class TestSuite(unittest.TestCase):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    test_dir = os.path.join(curr_dir, 'test_dir')
    all_expected_testcases = {
            'test_dir.deps.DemoCase0',
            'test_dir.deps.DemoCase1',
            'test_dir.deps.DemoCase2',
            'test_dir.deps.DemoCase3',
            'test_dir.deps.DemoCase4',
            'test_dir.inter_file_deps.DemoCase10',
            'test_dir.inter_file_deps.DemoCase8',
            'test_dir.inter_file_deps.DemoCase9',
        }

    def test_suite_discover(self):
        suite = TestSuiteDemo1()
        suite.discover(self.test_dir)
        actual_testcases = set([ full_name for full_name, cls in suite.testcases ])
        self.assertEqual(actual_testcases, self.all_expected_testcases)

    def test_suite_build_deps_graph(self):
        suite = TestSuiteDemo1()
        suite.discover(self.test_dir)
        actual_testcases = set([ full_name for full_name, cls in suite.testcases ])
        self.assertEqual(actual_testcases, self.all_expected_testcases)
        graph = suite.get_deps_graph()

        expected_in = {'test_dir.deps.DemoCase0': set(),
                'test_dir.deps.DemoCase1': {'test_dir.deps.DemoCase0',
                    'test_dir.inter_file_deps.DemoCase8'},
                'test_dir.deps.DemoCase2': {'test_dir.deps.DemoCase0',
                    'test_dir.inter_file_deps.DemoCase9'},
                'test_dir.deps.DemoCase3': {'test_dir.deps.DemoCase1',
                    'test_dir.deps.DemoCase2',
                    'test_dir.inter_file_deps.DemoCase10'},
                'test_dir.deps.DemoCase4': {'test_dir.deps.DemoCase3'},
                'test_dir.inter_file_deps.DemoCase10': set(),
                'test_dir.inter_file_deps.DemoCase8': set(),
                'test_dir.inter_file_deps.DemoCase9': set()}

        expected_out = {'test_dir.deps.DemoCase0': {'test_dir.deps.DemoCase1',
            'test_dir.deps.DemoCase2'}, 'test_dir.deps.DemoCase1':
            {'test_dir.deps.DemoCase3'}, 'test_dir.deps.DemoCase2':
            {'test_dir.deps.DemoCase3'}, 'test_dir.deps.DemoCase3':
            {'test_dir.deps.DemoCase4'}, 'test_dir.deps.DemoCase4': set(),
            'test_dir.inter_file_deps.DemoCase10': {'test_dir.deps.DemoCase3'},
            'test_dir.inter_file_deps.DemoCase8': {'test_dir.deps.DemoCase1'},
            'test_dir.inter_file_deps.DemoCase9': {'test_dir.deps.DemoCase2'}}

        self.assertEqual(graph._nodes.keys(), self.all_expected_testcases)
        self.assertEqual(graph._in, expected_in)
        self.assertEqual(graph._out, expected_out)

if __name__ == '__main__':
    unittest.main(verbosity = 0)
