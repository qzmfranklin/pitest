import os
import pitest
import unittest

# A -> B: A depends on B
#       -> 6      8
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
    deps = [ 'DemoCase1' ]
class DemoCase7(CaseBase1):
    deps = [ 'DemoCase2' ]
class DemoCase8(CaseBase1):
    deps = [ 'DemoCase3' ]

class Case(pitest.TestCase):
    _internal_deps = {
            'a0': [ 'a*' ],
            'a1': [ 'a2' ],
            'a2': [ 'b0', 'b2' ],
            'b0': [ 'b2', 'c1' ],
            'b1': [ 'b2', 'c0' ],
            'b2': [ 'c0' ],
            'c0': [ 'c1' ],
    }
    def test_a0():
        pass
    def test_a1():
        pass
    def test_a2():
        pass
    def test_b0():
        pass
    def test_b1():
        pass
    def test_b2():
        pass
    def test_c0():
        pass
    def test_c1():
        pass

class TestDeps(unittest.TestCase):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    this_basename = os.path.basename(__file__)
    prefix = pitest.PyName.to_pyname(this_basename)

    def test_deps_graph_for_suite(self):
        testcases = [ pitest.PyName(self.prefix, cls) for cls in [
                DemoCase0, DemoCase1, DemoCase2,
                DemoCase3, DemoCase4, DemoCase5,
                DemoCase6, DemoCase7, DemoCase8,
            ]
        ]
        expected_outlist = {
                'test_deps.DemoCase0': {'test_deps.DemoCase1', 'test_deps.DemoCase2'},
                'test_deps.DemoCase1': {'test_deps.DemoCase3'},
                'test_deps.DemoCase2': {'test_deps.DemoCase3'},
                'test_deps.DemoCase3': {'test_deps.DemoCase4'},
                'test_deps.DemoCase4': set(),
                'test_deps.DemoCase5': {'test_deps.DemoCase0', 'test_deps.DemoCase6', 'test_deps.DemoCase7'},
                'test_deps.DemoCase6': {'test_deps.DemoCase1'},
                'test_deps.DemoCase7': {'test_deps.DemoCase2'},
                'test_deps.DemoCase8': {'test_deps.DemoCase3'},
        }
        graph = pitest.Deps.deps_graph_for_suite(testcases)
        actual_outlist = graph._out
        self.assertEqual(expected_outlist, actual_outlist)

    def test_deps_graph_for_case(self):
        class_name_obj = pitest.PyName(self.prefix, Case)
        graph = pitest.Deps.deps_graph_for_case(class_name_obj)
        expected_outlist = {
                'test_deps.Case.test_a0': {'test_deps.Case.test_a1', 'test_deps.Case.test_a2'},
                'test_deps.Case.test_a1': {'test_deps.Case.test_a2'},
                'test_deps.Case.test_a2': {'test_deps.Case.test_b0', 'test_deps.Case.test_b2'},
                'test_deps.Case.test_b0': {'test_deps.Case.test_b2', 'test_deps.Case.test_c1'},
                'test_deps.Case.test_b1': {'test_deps.Case.test_b2', 'test_deps.Case.test_c0'},
                'test_deps.Case.test_b2': {'test_deps.Case.test_c0'},
                'test_deps.Case.test_c0': {'test_deps.Case.test_c1'},
                'test_deps.Case.test_c1': set(),
        }
        actual_outlist = graph._out
        self.assertEqual(expected_outlist, actual_outlist)

if __name__ == '__main__':
    unittest.main(verbosity = 0)
