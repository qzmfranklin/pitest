import pprint
import sys

class Py3DAGError(Exception):
    pass

class DAG(object):
    """Directed Acyclic Graph, used by pitest.Scheduler.
    """

    def __init__(self):
        """
        _nodes :
            { id : data }
            id:   an id to uniquely identify the node in a graph
            data: data associated with the node
            
            NOTE: ids can be any type. Recommend using either str or int
            consistently in your own case.

        _in, _out:
            _in:  incoming edges, { 'a' : { 'b', 'c' } } means a <- b, c.
            _out: outgoing edges, { 'a' : { 'b', 'c' } } means a -> b, c.

        Methods whose name begin with add_ and del_ guarantee to leave the
        graph object in a consistent state, and/or the graph is a dag, provided
        that the object was in a consistent state, and/or the graph was a dag
        before the method is called.
        """
        self._nodes = {}
        self._in = {}
        self._out = {}

    def print_debug(self, fd = sys.stdout):
        """ Print internal data to file. """
        pprint.pprint(self._nodes)
        pprint.pprint(self._in)
        pprint.pprint(self._out)

    def clear(self):
        """ Reset graph to empty. """
        self._nodes = {}
        self._in = {}
        self._out = {}

    def get_data(self, id):
        """ Get data associated with id. """
        return self._nodes[id]

    @property
    def sources(self):
        """ source: a node which has no incoming edges """
        sources = []
        for id, in_list in self._in.items():
            if len(in_list) == 0:
                sources.append(id)
        return sources

    @property
    def sinks(self):
        """ sink: a node which has no outgoing edges """
        sinks = []
        for id, out_list in self._out.items():
            if len(out_list) == 0:
                sinks.append(id)
        return sinks

    @property
    def isolated_nodes(self):
        """ nodes that are not connected to any other node """
        return self.sources & self.sinks

    def add_node(self, id, data = None, *, dup = 'error'):
        """
        Args:
            dups: one of [ 'error', 'ignore', 'overwrite' ], the action in case
                the same id already exists.
        """
        if id in self._nodes:
            if dup == 'error':
                raise Py3DAGError("Node with id = '{}' already exists.".format(id))
            elif dup == 'ignore':
                return
            elif dup == 'overwrite':
                pass
            else:
                dups = [ 'error', 'ignore', 'overwrite' ]
                raise Py3DAGError("Keyword argument 'dup' must be one of {}".format(dups))
        self._nodes[id] = data
        self._in[id]  = set()
        self._out[id] = set()

    def del_node(self, id, noexist_ok = False):
        """ Delete node from graph.

        Args:
            noexist_ok: Do not raise error when deleing non-existing node.

        Raises:
            Py3DAGError: Delete non-existing node.
        """

        if not id in self._nodes:
            if not noexist_ok:
                raise Py3DAGError("Node with id = '{}' does not exist.".format(id))
            else:
                return

        del self._nodes[id]
        del self._in[id]
        del self._out[id]
        for local_id, out_list in self._out.items():
            out_list.discard(id)

    def add_edge(self, src_id, dst_id, *, exist_ok = False, backedge_ok = False):
        """ Add edge to graph.

        Add edge src_id -> dst_id.
        No-op if src_id == dst_id.

        Raises:
            Py3DAGError if this is a backedge.
        """
        if src_id == dst_id:
            return
        if not exist_ok and dst_id in self._out[src_id]:
            raise Py3DAGError("Edge '{}' -> '{}' already exists.".format(src_id, dst_id))
        if not backedge_ok and src_id in self._out[dst_id]:
            raise Py3DAGError("Cannot add backedge '{}' -> '{}'.".format(src_id, dst_id))
        self._in[dst_id].add(src_id)
        self._out[src_id].add(dst_id)

    def add_edges(self, src_ids, dst_ids, **kwargs):
        for src in src_ids:
            for dst in dst_ids:
                self.add_edge(src, dst, **kwargs)

    def del_edge(self, src_id, dst_id, noexist_ok = False):
        if noexist_ok:
            self._in[dst_id].discard(src_id)
            self._out[src_id].discard(dst_id)
        else:
            self._in[dst_id].remove(src_id)
            self._out[src_id].remove(dst_id)

    def del_edges(self, src_ids, dst_ids, **kwargs):
        for src in src_ids:
            for dst in dst_ids:
                self.del_edge(src, dst, **kwargs)

    def check_acyclic(self):
        """
        return:
            None if the graph is acyclic, or
            a tuple of node ids (u, v) upon discovery of the first backedge.

        Algorithm: Depth first traversal of graph, look for backedge.

        vflags: visitation flags of nodes.
            white = untouched
            grey  = pushed stack
            black = visited

        sources: nodes with no incoming edges.
        """
        vflags = {}
        for id in self._nodes:
            vflags[id] = 'white'
        sources = self.sources
        for id in sources:
            if not id in vflags or vflags[id] == 'black':
                continue
            if vflags[id] == 'grey':
                raise Py3DAGError("A source node '{}' is grey".format(id))
            stack = [id]
            vflags[id] = 'grey'
            while len(stack) != 0:
                curr = stack.pop()
                vflags[curr] = 'black'
                for child in self._out[curr]:
                    if vflags[child] == 'white':
                        stack.append(child)
                        vflags[child] = 'grey'
                    elif vflags[child] == 'black':
                        continue
                    elif vflags[child] == 'grey':
                        return (curr, child)
                    else:
                        raise Py3DAGError("Unknown vflag '{}'. Can only be 'white', 'grey', or 'black'")
        return None
