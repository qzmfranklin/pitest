import copy

class TestCaseResult(object):

    """Container of test results of a test case.

    In this class, test methods are sometimes referred to as 'test'. Test cases
    are always referred to as 'test cases'.

    Attributes:
        _testcase: Name of the test case.
        _success: List of test methods that are completed successfully.
        _failure: A dicionary of failed test methods with their corresponding
            error objects.
        _blocked_tests: A dicionary mapping test methods that are directly
            blocked by failed tests. Test methods that are not run but not
            directly blocked by any failed test method are not included here.
        _unknown_tests: A list of test methods that are not run but do not have
            failed prerequisites.
    """

    def __init__(self, testcase_name):
        self._testcase = testcase_name
        self._success = []
        self._failure = {}
        self._blocked_tests = {}
        self._unknown_tests = []

    def add_success(self, test):
        """Add a test method to the list of successful tests. """
        self._success.append(test)

    def add_failure(self, test, retval):
        """Add a test method to the list of failed tests. """
        self._failure[test] = retval

    def set_blocked_tests(self, blocked_tests):
        """Set blocked test methods.

        Blocked test method: Test method that is not run because it has failed
        prerequisite(s).
        
        Args:
            blocked_test: A dictionary mapping blocked tests to their blocking
                tests. For example, { 'foo': {'bar', 'dir'} }
        """
        self._blocked_tests = copy.deepcopy(blocked_tests)

    def set_unknown_tests(self, unknown_tests):
        """Add unknown test methods.

        Unknown test method: Test method that is not run but does not have
        failed prerequisites.

        Args:
            unkonwn_test: A list of unkown test methods.
        """
        self._unknown_tests = copy.deepcopy(unknown_tests)

    @property
    def success(self):
        """Is all tests successfully finished?"""
        return len(self._failure) == 0 and len(self._blocked_tests) == 0

    def __str__(self):
        out = '{}: finished {} tests\n'.format(
                self._testcase, len(self._success))

        if self._failure:
            out += '    FAILURE: {}\n'.format(len(self._failure))
            info_list = []
            for test_name, error_msg in sorted(self._failure.items()):
                msg = '        {}.{}: {}\n'.format(
                        self._testcase, test_name, error_msg)
                info_list.append(msg)
            out += ''.join(info_list)
            del info_list

        if self._blocked_tests:
            out += '    BLOCKED: {}\n'.format(len(self._blocked_tests))
            info_list = []
            for test_name, blocking_tests in sorted(self._blocked_tests.items()):
                blocking_list = []
                for blocking_test in blocking_tests:
                    blocking_list.append('{}.{}'.format(self._testcase, blocking_test))
                msg = "        {}.{}: {}\n".format(
                        self._testcase, test_name, sorted(blocking_list))
                info_list.append(msg)
            out += ''.join(info_list)
            del info_list

        if self._unknown_tests:
            out += '    UNKNOWN: {}\n'.format(len(self._blocked_tests))
            info_list = []
            for test_name in self._unknown_tests:
                msg = "        {}.{}\n".format(
                        self._testcase, test_name, sorted(blocking_list))
                info_list.append(msg)
            out += ''.join(info_list)
            del info_list

        return out

class TestSuiteResult(object):

    """Container of test results of a test suite.

    Attributes:
        _testsuite: Full name of the test suite.
        _args_obj: The argument object passed to test cases.
        _testcase_results: A list of TestCaseResult objects. This list only has
            results for test cases that are run - either successfully completed
            or failed. Test cases that are not run do not appear in this list.
        _blocked_testcases: A dictionary mapping test cases that are directly
            blocked by failed test cases to the blocking test cases. Test cases
            that are not run, but not directly blocked by a failed test case are
            not included here.
        _untouched_testcases: A list of test cases that are not run, but not
            blocked by any failed test cases.

            NOTE: The word 'untouched' also appeared in the scheduler but over
            there it means that the task not ready for running.
    """

    def __init__(self, testsuite_name, args_obj):
        self._testsuite = testsuite_name
        self._args_obj = args_obj
        self._testcase_results = []
        self._blocked_testcases = {}
        self._unknown_testcases = []

    def add_test_case_result(self, test_case_result):
        """Add a test case result."""
        self._testcase_results.append(test_case_result)

    def set_blocked_testcases(self, blocked_testcases):
        """Set the directly blocked test cases.

        Test cases that are not directly blocked by a failed test case should be
        set via set_unknown_testcases().

        Args:
            blocked_test: A dictionary mapping blocked tests to their blocking
                tests. For example, { 'foo': {'bar', 'dir'} }
        """
        self._blocked_testcases = blocked_testcases

    def set_unknown_testcases(self, unknown_testcases):
        """Set the list of indirectly blocked test cases. """
        self._unknown_testcases = unknown_testcases

    @property
    def success(self):
        """Is all test cases successfully finished?"""
        for result in self._testcase_results:
            if not result.success:
                return False
        return True

    @property
    def num_testcases(self):
        """Number of all test cases attempted.

        Inlucde test cases that are completed successfully, unseccessfully, or
        blocked by failed tests.
        """
        return self.num_success + self.num_failure + self.num_blocked + self.num_unknown

    @property
    def num_success(self):
        """Number of test cases that completed successfully."""
        retval = 0
        for result in self._testcase_results:
            if result.success:
                retval += 1
        return retval

    @property
    def num_failure(self):
        """Number of test cases that completed successfully."""
        return len(self._testcase_results) - self.num_success

    @property
    def num_blocked(self):
        """Number of test cases that are directly blocked by failed test cases."""
        return len(self._blocked_testcases)

    @property
    def num_unknown(self):
        """Number of test cases that are not run but not directly blocked."""
        return len(self._unknown_testcases)

    def __str__(self):
        out = ''
        out += '{}\n'.format(self._args_obj if self._args_obj else '(no args)')
        out += ''.join([ str(x) for x in self._testcase_results ])
        if self._blocked_testcases:
            for blocked_test, blocking_list in self._blocked_testcases.items():
                out += '{}: blocked by {}\n'.format(
                        blocked_test, sorted(blocking_list))
        out += '================================================================\n\n'
        if self.num_success != 0:
            out += 'SUCCESS: {}\n'.format(self.num_success)
        if self.num_failure != 0:
            out += 'FAILURE: {}\n'.format(self.num_failure)
        if self.num_blocked != 0:
            out += 'BLOCKED: {}\n'.format(self.num_blocked)
        if self.num_unknown != 0:
            out += 'UNKNOWN: {}\n'.format(self.num_unknown)
        out += '\n'
        out += 'PASS\n' if self.success else 'FAIL\n'
        return out
