from . import dag

import fnmatch
import inspect
import re

class TestCaseBase(object):
    """Base test case class.

    Terminology:
        test method: A test method is a method whose name matches at least one
            pattern in test_patterns.

    Attributes:
        test_patterns: List of glob patterns matching test methods in this test
            case.
        setup(), teardown(): Run before/after each test method.
        setup_instance(), teardown_instance(): Run before/after all test methods
            in this test case.
        deps: A list glob pattern strings. Test cases matching any of the
            patterns are treated as prerequisites of this test case. The
            discover module uses the directory hierarchy to create namespaces
            for loaded test cases. You can reference a module by part of its
            full name.
                Example:
                    deps = [ 'foo.bar.TestCase*' ]
            When building the dependency graph using get_deps_graph(), if a
            partial name resolves to more than one loaded test case, an error is
            raised. See more about namespace and resolution, please refer to
            Discover.discover.__doc__ in discover.py.
        internal_deps: Dependencies between test methods in this test case,
            stored as a dictionary that maps targets to prerequisites. Support
            glob patterns.
                Example:
                    { 'test_foo*' : [ 'test_bar*', 'test_foo*bar' ] }
    """

    deps = []
    internal_deps = {}
    test_patterns = [ 'test_*', ]

    def setup(self, *args, **kwargs):
        pass

    def teardown(self, *args, **kwargs):
        pass

    def setup_instance(self, *args, **kwargs):
        pass

    def teardown_instance(self, *args, **kwargs):
        pass

    def get_deps_graph(self) -> dag.DAG:
        """Build dependency graph for test methods.

        Returns:
            the dependency graph from on internal_deps. Nodes in the graph are
            2-tuples (metohd_name, method).

        Attributes:
            internal_deps: maps a target to its prerequsite(s). Glob wildcard is
            supported for targets and prerequisites.

        Raises:
            Py3DAGError: When cyclic dependency is detected, with the exception
            of self-dependency.
        """
        graph = dag.DAG()
        for test in self._get_all_tests():
            graph.add_node(*test)
        for src_pattern, dst_pattern_list in self.internal_deps.items():
            src_reg = fnmatch.translate(src_pattern)
            for dst_pattern in dst_pattern_list:
                dst_reg = fnmatch.translate(dst_pattern)
                # Add edges (src -> dst) to graph
                for src in graph._nodes.keys():
                    for dst in graph._nodes.keys():
                        if src == dst: # Ignore self dependency.
                            continue
                        if re.match(src_reg, src) and re.match(dst_reg, dst):
                            graph.add_edge(src, dst)
        return graph

    def _get_all_tests(self):
        """
        Return a list of (name, method) tuples whose names match one or more of
        the patterns listed in TestCaseBase.test_patterns.

        The returned methods are bound to the instance of the test case
        subclass and are callable.

        This method allows TestSuiteBase to know what test methods are available
        in this test case.
        """
        test_methods = []
        for pattern in TestCaseBase.test_patterns:
            reg_pattern = fnmatch.translate(pattern)
            cls_methods = inspect.getmembers(self, inspect.ismethod)
            for name, cls in cls_methods:
                if re.match(reg_pattern, name):
                    test_methods.append((name, cls))
        return test_methods

    @classmethod
    def _get_all_tests_class(self_cls):
        """
        Return a list of (name, method) tuples whose names match one or more of
        the patterns listed in TestCaseBase.test_patterns.

        The returned methods are NOT bound to the instance of the test case
        subclass and are callable.
        """
        test_methods = []
        for pattern in self_cls.test_patterns:
            reg_pattern = fnmatch.translate(pattern)
            cls_methods = inspect.getmembers(self_cls, inspect.isfunction)
            for name, cls in cls_methods:
                if re.match(reg_pattern, name):
                    test_methods.append((name, cls))
        return test_methods
