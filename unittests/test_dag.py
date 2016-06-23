import pitest
import unittest

class TestDag(unittest.TestCase):

    def test_dag(self):
        # Create graph
        graph = pitest.Dag()

        # Add nodes
        for i in range(5):
            graph.add_node(i)

        # Add edges
        graph.add_edges([ 0 ], [ 1, 2, 3, 4 ])
        graph.add_edges([ 1 ], [ 2, 3, 4 ])
        graph.add_edges([ 2 ], [ 3, 4 ])
        graph.add_edges([ 3 ], [ 4 ])

        # Find the sources and sinks
        self.assertEqual(set(graph.sources), {0})
        self.assertEqual(set(graph.sinks), {4})

        # Add a backedge, can detect the cycle
        graph.add_edges([ 3 ], [ 2 ], backedge_ok = True)
        self.assertEqual(set(graph.check_acyclic()), {3, 2})

        # Remove the backedge, is acyclic now
        graph.del_edges([ 3 ], [ 2 ])
        self.assertEqual(graph.check_acyclic(), None)

if __name__ == '__main__':
    unittest.main(verbosity = 0)
