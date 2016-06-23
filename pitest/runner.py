from . import deps
from . import result
from . import scheduler

import traceback

class Runner0(object):

    """Sequential runner class.

    This is the dumb runner class.
    """

    def run_many(case_nos, *, args_obj = None, respect_deps = True,
            visitor_func = None):
        """Run many test cases.

        Arguments:
            case_nos: A list/set of PyName instances servicing test case
                classes.
            args_obj: The Args object used to run the test methods.
            respect_deps: Respect dependency, as specified by TestCase.deps and
                TestCase._internal_deps.
            visotor_func: A function taking a case_no as argument. The visitor
                function. Run prior to running the case.

        Returns:
            A newly-created SuiteResult object that has all information about
            this run.
        """
        graph = deps.Deps.deps_graph_for_suite(case_nos)
        sched = scheduler.Scheduler(graph, deepcopy = True)
        csd = {} # crd = dictionary of case results
        while sched.available_tasks:
            task_id = sorted(sched.available_tasks)[0]
            sched.fetch_task(task_id)
            case_no = graph.get_data(task_id)
            if visitor_func:
                visitor_func(case_no)
            if task_id in csd:
                raise SchedulerError("The task '{}' already ran.".
                        format(task_id))
            csd[task_id] = Runner0.run_one(case_no, args_obj = args_obj)
            sched.deliver_task(task_id)

        return result.SuiteResult.from_data(scheduler = scheduler, csd = csd)

    def run_one(case_no, *, args_obj = None):
        """Run all test methods for one test case.

        Returns:
            An newly-created CaseResult object that has all information about
            this run.

        Args:
            graph: A dag.Dag instance whose nodes are (name, PyName), and the
                PyName instances service test methods of test cases.
            args_obj: An instance of Args. The default, None, means no
                arguments.
        """
        graph = deps.Deps.deps_graph_for_case(case_no)
        args, kwargs = ((), {}) if args_obj is None \
                else args_obj.get_method_args('__init__')
        case_instance = case_no.obj(*args, **kwargs)
        del args, kwargs

        sched = scheduler.Scheduler(graph, deepcopy = True)
        failure_msgs = {}

        Runner0.__call(case_instance.setup_instance, args_obj)
        while sched.available_tasks:
            task_id = sorted(sched.available_tasks)[0]
            sched.fetch_task(task_id)
            test_method = case_instance._get_method_by_name(task_id)
            try:
                Runner0.__call(case_instance.setup, args_obj)
                failure_msg = Runner0.__call(test_method, args_obj)
                if failure_msg is None:
                    sched.deliver_task(task_id)
                else:
                    sched.fail_task(task_id)
                Runner0.__call(case_instance.teardown, args_obj)
            except Exception as e:
                failure_msg = traceback.format_exc()
                sched.fail_task(task_id, is_exception = True)
            finally:
                if not failure_msg is None:
                    if task_id in failure_msgs:
                        raise SchedulerError("The task '{}' already failed.".
                                format(task_id))
                    failure_msgs[task_id] = failure_msg
        Runner0.__call(case_instance.teardown_instance, args_obj)

        return result.CaseResult.from_data(sheduler = sched,
                failure_msgs = failure_msgs)

    def __call(method, args_obj):
        """Call the method with the given argument.
        Return what the method returns.
        Raise what the method raises.
        """
        if args_obj is None:
            return method()
        else:
            return args_obj.call_method(method)
