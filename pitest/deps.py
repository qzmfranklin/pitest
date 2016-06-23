from . import case
from . import dag
from . import name

import fnmatch
import re

class Deps(object):

    @staticmethod
    def deps_graph_for_suite(case_nos, *, respect_deps = True):
        """Build dependency graph among test cases.

        TestCase.deps are used to construct the Dag.

        Arguments:
            case_nos: A list/set of PyName instances servicing TestCase classes.
            respect_deps: Respect TestCase.deps.

        Returns:
            A dag.Dag object whose nodes are (name, PyName) tuples.
        """
        graph = dag.Dag()
        for case_no in case_nos:
            graph.add_node(case_no.name, case_no)

        if not respect_deps:
            return graph

        for src in case_nos:
            case_cls = src.obj
            for dst_pat in case_cls.deps:
                for dst_name, dst in graph._nodes.items():
                    if dst.match(dst_pat):
                        graph.add_edge(src.name, dst.name)

        return graph

    @staticmethod
    def deps_graph_for_case(case_no, *, respect_deps = True):
        """Build the dependency graph for the test case class.

        TestCase._internal_deps are used to construct the Dag. Note that
        _internal_deps omit the common prefix to test methods.

        Arguments:
            case_no: An PyName instance servicing a TestCase class.
            respect_deps: Respect TestCase._internal_deps

        Returns:
            A dag.Dag object whose nodes are (name, PyName) tuples.
        """
        case = case_no.obj    # the test case class object

        graph = dag.Dag()
        for test in case._get_test_method_names_class():
            obj = case_no.sub(test)
            graph.add_node(obj.name, obj)

        if not respect_deps:
            return graph

        # Variables:
        #     src, dst: PyName instances representing the source node and the
        #       destination node, respectively.
        #     prefix: The common prefix to test methods in pitest.TestCase.
        #     src0, dst_pat0: The source name and the destination pattern,
        #       respectively, i.e., without the prefix or full path.
        #     dst_name: The full destination name.
        from .case import TestCase
        prefix = TestCase._test_method_prefix

        import sys
        for src0, dst_pats in case._internal_deps.items():
            srcs = case_no.subglob(prefix + src0)
            for dst_pat0 in dst_pats:
                dst_pat = prefix + dst_pat0
                for dst_name, dst in graph._nodes.items():
                    # Ignore self dependency
                    for src in srcs:
                        if src.name != dst.name and dst.match(dst_pat):
                            graph.add_edge(src.name, dst.name)

        return graph
