from . import dag

import copy

class SchedulerError(Exception):
    pass

class Scheduler(object):
    """
    A dynamic scheduler based on directed acyclic graph (DAG).
    
    An edge A -> B is interpreted as 'A depends on B.'

    Attributes:
        _dag: An dag.DAG object.
        _task_status: A dicitonary holding the status of tasks.
        _available_tasks: Tasks that can run concurrently.
        _blocked_tasks: Dicionary mapping blocked tasks to their blocking tasks.
    """

    _status_set = { 'untouched', 'fetched', 'delivered', 'failed' }

    def __init__(self, deps_graph: dag.DAG, *, deepcopy = True):
        """
        deps_graph:
            Must be dag.DAG object.
            Access the 'private' fields in dag.DAG.
            Used in a read-only manner.

        deepcopy:
            Deep copy the deps_graph, just in case the graph is altered
            unexpected. Safe to not use deepcopy if the graph will not be
            altered during the lifetime of this scheduler object.
        """
        self._dag = copy.deepcopy(deps_graph) if deepcopy else deps_graph
        self._task_status = {}
        for id in self._dag._nodes:
            self._task_status[id] = 'untouched'
        self._available_tasks = set(self._dag.sinks)
        self._blocked_tasks = dict()

    def reset(self):
        """
        Reset scheduler to the same status after __init__().
        """
        self._change_status('untouched')
        self._available_tasks = set(self._dag.sinks)
        self._blocked_tasks = dict()

    @property
    def available_tasks(self):
        return self._available_tasks

    @property
    def blocked_tasks(self):
        return self._blocked_tasks

    @property
    def unknown_tasks(self):
        """A list of tasks that are indirectly blocked.

        Tasks that have failed prerequisites are blocked tasks. Unknown tasks
        are those tasks all of whose prerequisite are either blocked or unknown.
        If a blocked task has any failed prerequisites, it is a blocked task,
        not an unknown task.
        """
        pool = []
        for task_id, status in self._task_status.items():
            if status == 'untouched' and not task_id in self.blocked_tasks:
                pool.append(task_id)
        return pool

    def fetch_task(self, task_id, *, fetched_ok = False, failed_ok = False):
        """Atomically mark a task as fetched.

        fetched_ok, delivered_ok, failed_ok:
            Do not raise error if the task is already fetched or delivered,
            respectively.

        If the task_id is 'failed' and failed_ok is True,
            - remove task_id from lists of blocking tasks in blocked_tasks, and
            - add task_id back to available_tasks.

        Raises:
            SchedulerError: if the task if already fetched or delivered.
        
        NOTE:
            fetch_task() does not remove task from the available_tasks. Tasks
            are removed from available_tasks when they are delivered or failed.
        """
        if not fetched_ok and self._task_status[task_id] == 'fetched':
            raise SchedulerError("Cannot fetch a fetched task '{}' without fetched_ok".format(task_id))
        if self._task_status[task_id] == 'delivered':
            raise SchedulerError("Cannot fetch a delivered task '{}' without delivered_ok".format(task_id))
        if self._task_status[task_id] == 'failed':
            if not failed_ok:
                raise SchedulerError("Cannot fetch a failed task '{}' without failed_ok".format(task_id))
            tmp = copy.deepcopy(self.blocked_tasks)
            for blocked_task_id, blocking_set in tmp.items():
                blocking_set.discard(task_id)
                if len(blocking_set) == 0:
                    del self._blocked_tasks[blocked_task_id]
            self._available_tasks.add(task_id)
        self._task_status[task_id] = 'fetched'

    def deliver_task(self, task_id, *, nofetch_ok = False):
        """Atomically mark a previously fetched task as delivered.

        Remove task_id from available_tasks, add its depending tasks to
        available_tasks if all prerequisites of the depending task are
        delivered.

        Args:
            nofetch_ok: Do not raise error if the task being delivered is not
                fetched. 

        Raises:
            SchedulerError: if the task being delivered was not previously
                fetched, or is already delivered or failed.
        """
        if not nofetch_ok and self._task_status[task_id] != 'fetched':
            raise SchedulerError("Cannot deliver a task (id = '{}') that was not previously fetched."
                    .format(task_id))
        self._task_status[task_id] = 'delivered'
        self._available_tasks.remove(task_id)
        for parent in self._dag._in[task_id]:
            is_ready = True
            for child in self._dag._out[parent]:
                if self._task_status[child] != 'delivered':
                    is_ready = False
                    break
            if is_ready:
                self._available_tasks.add(parent)

    def fail_task(self, task_id, *, nofetch_ok = False):
        """Atomically mark a previously fetched task as failed.

        Remove task_id from available_tasks, add its depending tasks to
        blocked_tasks.

        Args:
            nofetch_ok: Do not raise error if the task being failed is not
                fetched.

        Raises:
            SchedulerError: if the task being failed was not previously fetched,
                or is already delivered or failed.
        """
        if not nofetch_ok and self._task_status[task_id] != 'fetched':
            raise SchedulerError("Cannot fail a task (id = '{}') that was not previously fetched."
                    .format(task_id))
        self._task_status[task_id] = 'failed'
        self._available_tasks.remove(task_id)
        for parent in self._dag._in[task_id]:
            if parent in self._blocked_tasks:
                self._blocked_tasks[parent].add(task_id)
            else:
                self._blocked_tasks[parent] = { task_id }

    def fetch_tasks(self, task_ids, **kwargs):
        for id in copy.deepcopy(task_ids):
            self.fetch_task(id, **kwargs)
    
    def deliver_tasks(self, task_ids, **kwargs):
        for id in copy.deepcopy(task_ids):
            self.deliver_task(id, **kwargs)

    def fail_tasks(self, task_ids, **kwargs):
        for id in copy.deepcopy(task_ids):
            self.fail_task(id, **kwargs)

    def _change_status(self, status, *, task_id = None):
        """Internal helper for changing the status of a given task or all tasks.

        status:
            one of { 'untouched', 'fetched', 'delivered', 'failed' }

        task_id:
            None = all tasks.
        """
        if not status in Scheduler._status_set:
            raise SchedulerError("Unknown status '{}'. Must be {}".format(status, Scheduler._status_set))
        if task_id is None:
            for tid in self._task_status:
                self._task_status[tid] = status
        else:
            self._task_status[task_id] = status
