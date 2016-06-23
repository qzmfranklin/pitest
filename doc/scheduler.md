# py3-sched

> A python3 implementation of task scheduler based on directed acyclic graph.

## Algorithm

We denote 'A depends on B' or 'B is a prerequisite of A' as 'A -> B', where 'A'
and 'B' are nodes and '->' is the directed edge connecting A to B the in acyclic
directed graph (Dag). Hereafter, 'task' and 'node' are used interchangeably. The
word 'task' may mean either the node in the graph, or the actual task that is
scheduled by this scheduler.  The meaning should be clear from context unless
explicitly spoken.

An important use case of task scheduler is to allow parallel excecution of
tasks. We denote the set of tasks that can be executed concurrently as
@available_tasks. I will explain the algorithm used for finding the
@available_tasks at any given time.

At the beginning, all tasks are 'untouched'. The initial @available_tasks is
just the set of tasks that have no prerequisites, i.e., the set of sinks in the
Dag.

External processes/threads/functions can 'fetch' tasks from the initial
@available_tasks atomically and try to execute the fetched task. The 'fetch'
operation has to be atomic to avoid concurrency issues.

After a task is fetched, it is handed over to whoever claimed the fetch, called
the task handler. It is up to the task handler to execute the task, and to
decide whether it completed successfully in case the execution finished without
error. When a task is completed, successfully or not, the owning task handler
must 'deliver' the task or report 'fail' to the scheduler. Like 'fetch',
'deliver' and 'fail' must also be atomic.

When a task is 'deliver'ed to the scheduler, the scheduler does two things.
    - Remove the delivered task from @available_tasks, marking it as
      'delivered', so that it cannot be delivered or failed again.
    - Iterate through all the depending tasks of the delivered task, add to
      @available_tasks the ones all of whose prerequisites are delivered.

The scheduler associates @blocked_tasks with 'fail'. @blocked_tasks is a mapping
of tasks that are blocked by failed prerequisites to the list of blocking
prerequisites. Initially, @blocked_tasks is empty.

When a task is 'fail'ed, the scheduler does two things too.
    - Remove the failed task from @available_tasks, marking it as 'failed', so
      that it cannot be delivered or failed again.
    - Add all depending tasks of the failed task to @blocked_tasks.

## Re-fetch

- A delivered task cannot be fetched again.

- A fetched task can only be re-fetched with `fetched_ok = True`, e.g.,
  fetch_task(task_id, fetched_ok = True). In the later case, the re-fetch
  is a no-op.

- Multiple delivery of the same fetched task raises runtime error, unless
  used with `delivered_ok = True`. In the later case, the delivery is a no-op.

- A failed task can only be re-fetched with `failed_ok = True`.

- Re-fetching a failed task adds the task back to @available_tasks and causes
  @blocked_tasks to update accordingly. Thereofore, delivering a re-fetched task
  that is previously failed unblocks tasks that are previously blocked by this
  delivered task.

## Core API

`fetch_task()`:
        mark a task as 'fetched'

`deliver_task()`:
        mark a previously fetched task as 'delivered'

`fail_task()`:
        mark a previously fetched task as 'fail'

`available_tasks`:
        a property, the set of tasks that can run concurrently

`blocked_tasks`:
        a property, the set of tasks that cannot run because of failed
        prerequisites.

##  Dependencies

The scheduler uses a Dag class from py3_dag.py.

## TODO

- Make fetch_task(), deliver_task(), and fail_task() atomic.

## Unit Test

The unit test tests the Dag class and the core API of the scheduler class.

The test uses the unittest library.

How to run the test:
    `./tests.py`
