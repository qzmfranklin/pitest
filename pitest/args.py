import pprint

class ArgsError(Exception):
    pass

class Args(object):
    """Opaque argument object used by test suites and test cases.

    Attributes:
        _args, _kwargs: Dictionaries holding the positional and keyword
            arguments, respectively.
    """

    def __init__(self):
        self._args   = { '__init__': (), 'setup': (), 'teardown': (), 'test': (),'setup_instance': (), 'teardown_instance': (), }
        self._kwargs = { '__init__': {}, 'setup': {}, 'teardown': {}, 'test': {},'setup_instance': {}, 'teardown_instance': {}, }

    def get_method_args(self, method_name):
        """Get the (*args, **kwargs) tuple for a method.

        Args:
            method_name: Internally changed to 'test' if not one of { __init__,
                setup, teardown, setup_instance, teardown_instance }
        """
        if not method_name in self._args:
            method_name = 'test'
        return (self._args[method_name], self._kwargs[method_name])

    def set_method_args(self, method_name, *, args = None, kwargs = None):
        """Set positional and keyword arguments for method.

        Args:
            method_name: Must be one of { test, __init__, setup, teardown,
                setup_instance, teardown_instance }. Otherwise report error.
            args, kwargs: The positional arguments, in a tuple, and the keyword
                arguments, in a dictionary, respectively. None means do not set
                it up.
        """
        if not method_name in self._args:
            raise ArgsError('method_name {} is not one of {}'.format(method_name, self._args))
        if not args is None:
            self._args[method_name] = args
        if not kwargs is None:
            self._kwargs[method_name] = kwargs

    def call_method(self, method):
        """Call the method with arguments stored in this args object.

        Returns:
            Whatever the called method returns.

        Raises:
            Whatever the called method raises.

        Args:
            method_name: Internally changed to 'test' if not one of { __init__,
                setup, teardown, setup_instance, teardown_instance }
        """
        name = method.__name__
        if not name in self._args:
            name = 'test'
        args, kwargs = self.get_method_args(method.__name__)
        return method(*self._args[name], **self._kwargs[name])

    def __str__(self):
        args = {}
        kwargs = {}
        for method_name, arg in self._args.items():
            if arg:
                args[method_name] = arg
        for method_name, kwarg in self._kwargs.items():
            if kwarg:
                kwargs[method_name] = kwarg
        return 'args   = {}\nkwargs = {}'.format(
                pprint.pformat(args, indent = 4),
                pprint.pformat(kwargs, indent = 4))
