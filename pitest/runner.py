from . import result
from . import scheduler
from . import suite


import traceback

class Runner(object):

    @staticmethod
    def run_test_suite(suite, args_obj = None):
        """Run all test cases for the test suite.

        Returns:
            An newly-created TestSuiteResult object that has all information
            about this run.

        Args:
            suite: An instance of a subclass of pitest.TestSuiteBase.
            args_obj: An instance of Args.
        """
        res = result.TestSuiteResult(suite.__class__.__name__, args_obj)

        graph = suite.get_deps_graph()
        sched = scheduler.Scheduler(graph, deepcopy = False)
        args, kwargs = ((), {}) if args_obj is None else args_obj.get_method_args('__init__')
        while sched.available_tasks:
            task_id = sorted(sched.available_tasks)[0]
            sched.fetch_task(task_id)
            testcase_cls = graph.get_data(task_id)
            testcase_instance = testcase_cls(*args, **kwargs)
            testcase_result = Runner.run_test_case(testcase_instance, args_obj,
                    fullname = task_id)
            res.add_test_case_result(testcase_result)
            if testcase_result.success:
                sched.deliver_task(task_id)
            else:
                sched.fail_task(task_id)

        res.set_blocked_testcases(sched.blocked_tasks)
        res.set_unknown_testcases(sched.unknown_tasks)

        return res

    @staticmethod
    def run_test_case(case, args_obj = None, *, fullname = None):
        """Run all test methods for the test case.

        Returns:
            An newly-created TestCaseResult object that has all information
            about this run.

        Args:
            case: An instance of a subclass of pitest.TestCaseBase.
            args_obj: An instance of Args.
            fullname: The full name of the test case. If None, just use
                case.__class__.__name__.
        """
        testcase_name = fullname if fullname else case.__class__.__name__
        res = result.TestCaseResult(testcase_name)

        graph = case.get_deps_graph()
        sched = scheduler.Scheduler(graph, deepcopy = False)
        Runner._call_method_with_args(case.setup_instance, args_obj)
        while sched.available_tasks:
            task_id = sorted(sched.available_tasks)[0]
            sched.fetch_task(task_id)
            test_method = graph.get_data(task_id)
            Runner._call_method_with_args(case.setup, args_obj)

            retval = Runner._call_method_with_args(test_method, args_obj)
            if retval is None:
                sched.deliver_task(task_id)
                res.add_success(task_id)
            else:
                sched.fail_task(task_id)
                res.add_failure(task_id, retval)
            Runner._call_method_with_args(case.teardown, args_obj)
        Runner._call_method_with_args(case.teardown_instance, args_obj)

        res.set_blocked_tests(sched.blocked_tasks)
        res.set_unknown_tests(sched.unknown_tasks)

        return res

    @staticmethod
    def _call_method_with_args(method, args_obj):
        if args_obj is None:
            return method()
        else:
            return args_obj.call_method(method)
