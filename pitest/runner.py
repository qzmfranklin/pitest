from . import deps
from . import result
from . import scheduler
from . import suite

class Runner0(object):

    """Sequential runner class.

    """

    def run_many(case_nos, *, args_obj = None, respect_deps = True,
            visitor_func = None):
        """Run test cases while respecting their inter-dependencies.

        Arguments:
            case_nos: A list/set of PyName instances servicing test case
                classes.
            args_obj: The Args object used to run the test methods.
            respect_deps: Respect dependency, as specified by TestCase.deps and
                TestCase._internal_deps.
            visotor_func: A function taking a case_no as argument. The visitor
                function. Run prior to running the case.
        """
        graph = deps.Deps.deps_graph_for_suite(case_nos)
        sched = scheduler.Scheduler(graph, deepcopy = True)
        while sched.available_tasks:
            task_id = sorted(sched.available_tasks)[0]
            sched.fetch_task(task_id)
            case_no = graph.get_data(task_id)
            if visitor_func:
                visitor_func(case_no)
            Runner0.run_one(case_no, args_obj = args_obj)
            sched.deliver_task(task_id)

    def run_one(case_no, *, args_obj = None):
        """Run all test methods for the test case.

        Returns:
            An newly-created TestCaseResult object that has all information
            about this run.

        Args:
            graph: A dag.DAG instance whose nodes are (name, PyName), and the
                PyName instances service test methods of test cases.
            args_obj: An instance of Args. The default, None, means no
                arguments.
        """
        graph = deps.Deps.deps_graph_for_case(case_no)
        args, kwargs = ((), {}) if args_obj is None else args_obj.get_method_args('__init__')
        case_instance = case_no.obj(*args, **kwargs)
        del args, kwargs

        sched = scheduler.Scheduler(graph, deepcopy = True)
        Runner0._call_method_with_args(case_instance.setup_instance, args_obj)
        while sched.available_tasks:
            task_id = sorted(sched.available_tasks)[0]
            sched.fetch_task(task_id)
            test_method = case_instance._get_method_by_name(task_id)
            Runner0._call_method_with_args(case_instance.setup, args_obj)

            retval = Runner0._call_method_with_args(test_method, args_obj)
            if retval is None:
                sched.deliver_task(task_id)
                #res.add_success(task_id)
            else:
                sched.fail_task(task_id)
                #res.add_failure(task_id, retval)
            Runner0._call_method_with_args(case_instance.teardown, args_obj)
        Runner0._call_method_with_args(case_instance.teardown_instance, args_obj)

        #res.set_blocked_tests(sched.blocked_tasks)
        #res.set_unknown_tests(sched.unknown_tasks)

        #return res

    def _call_method_with_args(method, args_obj):
        if args_obj is None:
            return method()
        else:
            return args_obj.call_method(method)
