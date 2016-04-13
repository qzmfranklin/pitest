import contextlib
import io
import os
import pitest
import sys
import unittest

# A -> B: A depends on B
#          8      10
#            \      \
#             \      \
#              \      \
#   7 ---> 0 ---> 1 ---> 3 ---> 4
#    \       \        /
#     \       \      /
#      \       \    /
#       -> 9 ---> 2

class CaseBaseTmp(pitest.TestCase):
    pass
class DemoCase0(CaseBaseTmp):
    deps = [ 'DemoCase1', 'DemoCase2' ]
class DemoCase1(CaseBaseTmp):
    deps = [ 'DemoCase3' ]
class DemoCase2(CaseBaseTmp):
    deps = [ 'DemoCase3' ]
class DemoCase3(CaseBaseTmp):
    deps = [ 'DemoCase4' ]
class DemoCase4(CaseBaseTmp):
    pass
class DemoCase7(CaseBaseTmp):
    deps = [ 'DemoCase0', 'DemoCase9' ]
class DemoCase8(CaseBaseTmp):
    deps = [ 'DemoCase1' ]
class DemoCase9(CaseBaseTmp):
    deps = [ 'DemoCase2' ]
class DemoCase10(CaseBaseTmp):
    deps = [ 'DemoCase3' ]

class TestSuiteDemo1(pitest.TestSuiteBase):
    testcase_baseclasses = [ 'CaseBaseTmp' ]

class CaseBaseTmp2(pitest.TestCase):
    pass
class DemoCase12(CaseBaseTmp2):
    internal_deps = {
        'test_foo1': [ 'test_foo*' ],
        'test_foo2': [ 'test_bar*', 'test_cha2' ],
        'test_foo3': [ 'test_bar1', 'test_cha3' ],
        'test_foo4': [ 'test_bar2', 'test_cha1', 'test_cha3' ],
        'test_bar*': [ 'test_cha*' ],
        'test_bar1': [ 'test_bar2' ],
        'test_cha1': [ 'test_cha2' ],
        'test_cha2': [ 'test_cha3' ],
    }
    def test_foo1(self):
        print('test_foo1')
    def test_foo2(self):
        print('test_foo2')
    def test_foo3(self):
        print('test_foo3')
    def test_foo4(self):
        print('test_foo4')
    def test_bar1(self):
        print('test_bar1')
    def test_bar2(self):
        print('test_bar2')
    def test_cha1(self):
        print('test_cha1')
    def test_cha2(self):
        print('test_cha2')
    def test_cha3(self):
        print('test_cha3')

class TestSuiteDemo2(pitest.TestSuiteBase):
    testcase_baseclasses = [ 'CaseBaseTmp2' ]

class TestRunner(unittest.TestCase):
    # This test uses the golden file approach.

    def test_run_case(self):
        fname = os.path.relpath(__file__)
        suite = TestSuiteDemo2()
        suite.load_file(fname)
        expected_stdout = """\
test_cha3
test_cha2
test_cha1
test_bar2
test_bar1
test_foo2
test_foo3
test_foo4
test_foo1
"""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = pitest.Runner.run_test_suite(suite)
        self.assertEqual(buf.getvalue(), expected_stdout)

    def test_run_suite(self):
        fname = os.path.relpath(__file__)
        suite = TestSuiteDemo1()
        suite.load_file(fname)
        result = pitest.Runner.run_test_suite(suite)
        expected_result_string = """\
(no args)
test_runner.DemoCase4: finished 0 tests
test_runner.DemoCase3: finished 0 tests
test_runner.DemoCase1: finished 0 tests
test_runner.DemoCase10: finished 0 tests
test_runner.DemoCase2: finished 0 tests
test_runner.DemoCase0: finished 0 tests
test_runner.DemoCase8: finished 0 tests
test_runner.DemoCase9: finished 0 tests
test_runner.DemoCase7: finished 0 tests
================================================================

SUCCESS: 9

PASS
"""
        self.assertEqual(str(result), expected_result_string)

if __name__ == '__main__':
    unittest.main(verbosity = 0)
