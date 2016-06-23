import pitest
import unittest

class TestScheduler(unittest.TestCase):
    sched = None

    @classmethod
    def setUpClass(cls):
        # Create graph
        graph = pitest.Dag()

        # Add nodes
        for i in range(5):
            graph.add_node(i)

        # Add edges
        graph.add_edges([ 0 ], [ 1, 2, 3, 4 ])
        graph.add_edges([ 1 ], [ 3, 4 ])
        graph.add_edges([ 2 ], [ 3, 4 ])
        graph.add_edges([ 3 ], [ 4 ])

        # Create scheduler
        cls.sched = pitest.Scheduler(graph)

    def test_fetch_and_deliver(self):
        sched = self.sched
        sched.reset()
        expected_taskpools = [ {4}, {3}, {1,2}, {0}, set() ]
        for expected_taskpool in expected_taskpools:
            actual_taskpool = sched.available_tasks
            self.assertEqual( actual_taskpool, expected_taskpool )
            sched.fetch_tasks(actual_taskpool)
            sched.deliver_tasks(actual_taskpool)

    def test_simple_fail(self):
        """
        Failing a task blocks its depending tasks.
        The blocked tasks know who are blocking them.
        """
        sched = self.sched
        sched.reset()

        expected_taskpools = [ {4}, {3} ]
        for expected_taskpool in expected_taskpools:
            actual_taskpool = sched.available_tasks
            self.assertEqual( actual_taskpool, expected_taskpool )
            sched.fetch_tasks(actual_taskpool)
            sched.deliver_tasks(actual_taskpool)

        # {0} -> {1, 2}
        actual_taskpool = sched.available_tasks
        self.assertEqual( actual_taskpool, {1, 2} )

        # delivering 1 does not block 0
        sched.fetch_tasks({1})
        sched.deliver_tasks({1})
        self.assertEqual( sched.blocked_tasks.keys(), set() )

        # failing 2 blocks 0
        sched.fetch_tasks({2})
        sched.fail_tasks({2})
        self.assertEqual( sched.blocked_tasks.keys(), {0} )

    def test_fail_and_retry(self):
        """
        A failed task can be re-fetched with failed_ok = True.
        Delivering a re-fetched task unblocks previously blocked tasks.
        """
        sched = self.sched
        sched.reset()

        expected_taskpools = [ {4}, {3} ]
        for expected_taskpool in expected_taskpools:
            actual_taskpool = sched.available_tasks
            self.assertEqual( actual_taskpool, expected_taskpool )
            sched.fetch_tasks(actual_taskpool)
            sched.deliver_tasks(actual_taskpool)

        # {0} -> {1, 2}
        actual_taskpool = sched.available_tasks
        self.assertEqual( actual_taskpool, {1, 2} )

        # delivering 1 does not block 0
        sched.fetch_tasks({1})
        sched.deliver_tasks({1})
        self.assertEqual( sched.blocked_tasks.keys(), set() )

        # failing 2 blocks 0
        sched.fetch_tasks({2})
        sched.fail_tasks({2})
        self.assertEqual( sched.blocked_tasks.keys(), {0} )

        # a successful retry of 2 unblocks 0, provided 1 is delivered
        sched.fetch_tasks({2}, failed_ok = True)
        sched.deliver_tasks({2})
        self.assertEqual( sched.blocked_tasks.keys(), set() )

if __name__ == '__main__':
    unittest.main(verbosity = 0)
