import inspect

class AssertionError(Exception):
    pass

class _TestCaseBase(object):
    """
    Internal base class servicing the TestCase class.
    """

    _test_method_prefix = 'test_'

    @classmethod
    def _get_test_method_names_class(cls):
        """Get names of test methods."""
        namelist = []
        cls_methods = inspect.getmembers(cls, inspect.isfunction)
        for name, method in cls_methods:
            if name.startswith(cls._test_method_prefix):
                namelist.append(name)
        return namelist

    def _get_method_by_name(self, fullname, default = None):
        """Get the method bound to self from name.

        Arguments:
            fullname: Full name. The last component is used to determine the
                method.
            default: If self does not have the attribute, the default object to
                return.
        """
        name = fullname.split('.')[-1]
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return default

    def assert_true(self, cond):
        if not bool(cond):
            raise AssertionError('assert_true() failed')

    def assert_false(self, cond):
        if bool(cond):
            raise AssertionError('assert_true() failed')

    def assert_equal(self, lhs, rhs):
        if not lhs == rhs:
            raise AssertionError('assert_equal() failed')

class TestCase(_TestCaseBase):
    """Base test case class.

    Terminology:
        test method: A test method is a method whose name matches at least one
            pattern in _test_patterns.

    Attributes:
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
            glob patterns and omit the common prefix 'test_'.
                Example:
                    { 'foo*' : [ 'bar*', 'foo*bar' ] }
        _test_method_prefix: The common prefix to test methods in the class.
    """

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
