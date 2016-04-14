from . import dag
from . import name

import fnmatch
import inspect
import re

class TestCase(object):
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
        _internal_deps: Dependencies between test methods in this test case,
            stored as a dictionary that maps targets to prerequisites. Support
            glob patterns.
                Example:
                    { 'test_foo*' : [ 'test_bar*', 'test_foo*bar' ] }
    """

    test_patterns = [ 'test_*', ]
    deps = []
    _internal_deps = {}

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
            The dependency graph from on _internal_deps. Nodes in the graph are
            2-tuples (metohd_name, method). The method names are not the full
            name, as serviced by the name.PyName class.

        Raises:
            Py3DAGError: When cyclic dependency is detected, with the exception
                of self-dependency.
        """
        graph = dag.DAG()
        for test in self._get_all_tests():
            graph.add_node(*test)
        for src_pat, dst_pat_list in self._internal_deps.items():
            for dst_pat in dst_pat_list:
                # Add edges (src -> dst) to graph
                for src in graph._nodes.keys():
                    for dst in graph._nodes.keys():
                        if src == dst: # Ignore self dependency.
                            continue
                        if fnmatch.fnmatchcase(src_pat, src) and fnmatch.fnmatchcase(dst_pat, dst):
                            graph.add_edge(src, dst)
        return graph

    @staticmethod
    def deps_graph_from_name_obj(testcase_name_obj) -> dag.DAG:
        """Build the dependency graph for the test case class.

        Returns:
            A dag.DAG object whose nodes are PyName instances servicing unbound
            methods of this test case class.
        """

    @classmethod
    def get_test_methods_class(cls):
        """
        Return a list of (name, method) tuples whose names match one or more of
        the patterns listed in TestCase.test_patterns.

        The returned methods are NOT bound to the instance of the test case
        subclass and are callable.
        """
        test_methods = []
        for pattern in cls.test_patterns:
            cls_methods = inspect.getmembers(cls, inspect.isfunction)
            for name, method in cls_methods:
                if fnmatch.fnmatchcase(pattern, name):
                    test_methods.append((name, method))
        return test_methods

    def _get_all_tests(self):
        """
        Return a list of (name, method) tuples whose names match one or more of
        the patterns listed in TestCase.test_patterns.

        The returned methods are bound to the instance of the test case
        subclass and are callable.

        This method allows TestSuiteBase to know what test methods are available
        in this test case.
        """
        test_methods = []
        for pattern in TestCase.test_patterns:
            reg_pattern = fnmatch.translate(pattern)
            cls_methods = inspect.getmembers(self, inspect.ismethod)
            for name, cls in cls_methods:
                if re.match(reg_pattern, name):
                    test_methods.append((name, cls))
        return test_methods

