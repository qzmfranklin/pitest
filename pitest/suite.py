from . import case
from . import dag
from . import discover

import inspect
import fnmatch
import re

class TestSuiteBaseError(Exception):
    pass

class NoTestCaseLoadedError(Exception):
    pass

class ReferenceUnloadedTestCaseError(Exception):
    def __init__(self, unloaded_testcases):
        self.unloaded_testcases = unloaded_testcases
        err_str = 'Cannot reference unloaded test cases: {}'.format(unloaded_testcases)
        super(Exception, self).__init__(err_str)

class TestSuiteBase(object):
    """Minimal base class of test suites.

    Attributes:
        testcase_baseclass: The base class name of test cases. Default is
            TestCaseBase.  Used in discover() and try_load_file() for
            selectively loading of test cases.
        testcases: A list of 2-tuples (full_cls_name, class).
    """

    testcase_baseclasses = [ case.TestCaseBase.__name__ ]

    def __init__(self):
        self._testcases = []

    @property
    def testcases(self):
        """A list of 2-tuples (full_cls_name, test_case_cls), readonly."""
        return self._testcases

    def discover(self, start_dir, *, recursive = True, pattern = '*.py',
            notestcase_ok = False):
        """Discover test cases starting from @start_dir.

        Args:
            recursive: True if discover test cases recursively. False otherwise.
            pattern: The glob pattern to match filenames.
            nocase_ok: OK if no test cases are discovered.

        Raises:
            DiscoverError: An error occurred when discovering tests.
            NoTestCaseLoadedError: No test case is loaded and notestcase_ok is
                False.
        """
        testcases = discover.Discover.discover(start_dir,
                baseclasses = self.testcase_baseclasses,
                recursive = recursive,
                pattern = pattern)
        if not testcases and not notestcase_ok:
            raise TestSuiteBaseError("suite.discover('{}') did not find any test cases.".format(start_dir))
        self._add_testcases(testcases)

    def load_file(self, fname, *, notestcase_ok = False):
        """Load test cases from a given file.

        Args:
            nocase_ok: OK if no test cases are discovered.

        Raises:
            DiscoverError: An error occurred when discovering tests.
            NoTestCaseLoadedError: No test case is loaded and notestcase_ok is
                False.
        """
        testcases = discover.Discover.load_file(fname,
                baseclasses = self.testcase_baseclasses)
        if not testcases and not notestcase_ok:
            raise NoTestCaseLoadedError(
                "suite.load_file('{}') did not find any test cases.".format(fname))
        self._add_testcases(testcases)

    def get_deps_graph(self) -> dag.DAG:
        """Build the dependency graph for all loaded test cases.

        Returns:
            A dependency graph, whose nodes are of 2-tuples of (full_cls_name,
            class). A full_cls_name looks like this:

                .full.path.to.this_module.this_class

        Attributes:
            self..deps: Dependencies are specified in deps, a class variable in
                test case classs. It supported glob pattern, e.g., 'FooClass1*'.

        TODO: Report error when trying to reference unloaded modules.
        """
        graph = dag.DAG()
        for fullname, test in self.testcases:
            graph.add_node(fullname, test)

        for fullname, test in self.testcases:
            for prerequisite_pattern in test.deps:
                reg_pattern = '^(({0})|(.*\.{0}))$'.format(prerequisite_pattern)
                for prerequisite in graph._nodes:
                    if re.match(reg_pattern, prerequisite):
                        graph.add_edge(fullname, prerequisite)

        return graph

    def _add_testcases(self, testcases):
        self._testcases += testcases

