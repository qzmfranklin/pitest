import contextlib
import io
import os
import pitest
import sys
import textwrap
import unittest

# A -> B: A depends on B
#
#       -> 6 ---> 8
#      /     \      \
#     /       \      \
#    /         \      \
#   5 ---> 0 ---> 1 ---> 3 ---> 4
#    \       \        /
#     \       \      /
#      \       \    /
#       -> 7 ---> 2
class CaseBase1(pitest.TestCase):
    pass
class DemoCase0(CaseBase1):
    deps = [ 'DemoCase1', 'DemoCase2' ]
class DemoCase1(CaseBase1):
    deps = [ 'DemoCase3' ]
class DemoCase2(CaseBase1):
    deps = [ 'DemoCase3' ]
class DemoCase3(CaseBase1):
    deps = [ 'DemoCase4' ]
class DemoCase4(CaseBase1):
    pass
class DemoCase5(CaseBase1):
    deps = [ 'DemoCase0', 'DemoCase6', 'DemoCase7' ]
class DemoCase6(CaseBase1):
    deps = [ 'DemoCase1', 'DemoCase8' ]
class DemoCase7(CaseBase1):
    deps = [ 'DemoCase2' ]
class DemoCase8(CaseBase1):
    deps = [ 'DemoCase3' ]

class CaseBase2(pitest.TestCase):
    pass
class DemoCase9(CaseBase2):
    _internal_deps = {
        'foo1': [ 'foo*' ],
        'foo2': [ 'foo3', 'foo4', 'bar*', 'cha2' ],
        'foo3': [ 'foo4', 'bar1', 'cha3' ],
        'foo4': [ 'bar2', 'cha1', 'cha3' ],
        'bar*': [ 'cha*' ],
        'bar1': [ 'bar2' ],
        'cha1': [ 'cha2' ],
        'cha2': [ 'cha3' ],
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

class TestRunner(unittest.TestCase):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    this_basename = os.path.basename(__file__)
    prefix = pitest.PyName.to_pyname(this_basename)

    def test_run_many(self):
        case_nos = [ pitest.PyName(self.prefix, cls) for cls in [
                DemoCase0, DemoCase1, DemoCase2,
                DemoCase3, DemoCase4, DemoCase5,
                DemoCase6, DemoCase7, DemoCase8,
            ]
        ]

        print_name = lambda case_no : print(case_no.name)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = pitest.Runner0.run_many(case_nos, visitor_func = print_name)
            output = buf.getvalue()
            expected = textwrap.dedent('''\
                    test_runner.DemoCase4
                    test_runner.DemoCase3
                    test_runner.DemoCase1
                    test_runner.DemoCase2
                    test_runner.DemoCase0
                    test_runner.DemoCase7
                    test_runner.DemoCase8
                    test_runner.DemoCase6
                    test_runner.DemoCase5
                    ''')
            self.assertEqual(expected, output)

    def test_run_one(self):
        case_no = pitest.PyName(self.prefix, DemoCase9)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = pitest.Runner0.run_one(case_no)
            output = buf.getvalue()
            expected = textwrap.dedent('''\
                    test_cha3
                    test_cha2
                    test_cha1
                    test_bar2
                    test_bar1
                    test_foo4
                    test_foo3
                    test_foo2
                    test_foo1
                    ''')
            self.assertEqual(expected, output)

if __name__ == '__main__':
    unittest.main(verbosity = 0)
