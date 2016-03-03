from . import args

import fnmatch
import re

class MainError(Exception):
    pass

class Main(object):
    """Helper class for __main__.py
    """

    @staticmethod
    def find_all_test_cases_by_name(testcase_name, testcases):
        """Look up testcase_name in testcases.

        Args:
            testcase_name: string, name of the test case.
            testcases: list or set of (full_cls_name, cls) tuples.

        Returns:
            All 2-tuples of (full_cls_name, cls) who names match the given name. If
            no match is found, return empty list.
        """
        reg = fnmatch.translate('*' + testcase_name)
        retval = []
        for name, cls in testcases:
            if re.match(reg, name):
                retval.append((name, cls))
        return retval

    @staticmethod
    def get_args_obj_from_source_code(source_code, *, args_name):
        """Get the args object from source code.

        The default name of the args object is stored in a variable:
                __pitest_main_default_args_name__ = 'my_args'
        In the above example, if @args_name is None, my_args is returned.

        If args_name is a string, for example, args_name = 'new_args', then an
        object named 'new_args' from the given @source_code is returned.

        If __pitest_main_default_args_name__ is not defined in @source_code,
        raises error.

        Returns:
            A instance of pitest.TestCaseArgs.

        Args:
            source_code: python3 code that defines the args object. The source
                code can define one or more args objects. The source code must
                define a string object named '__pitest_main_default_args_name__'
                and define an pitest.TestCaseArgs object whose name is the value
                of __pitest_main_default_args_name__.
            args_name: A string, the name of the pitest.TestCaseArgs object to
                return. Override the one specified by
                __pitest_main_default_args_name__ in the source code.
                None = do not override __pitest_main_default_args_name__.

        Raises:
            Whatever exceptions exec(source_code) raises.
            MainError: If __pitest_main_default_args_name__ is not defined in
                source code, or if the source code does not define object with
                the given name, or if the retrieved object is not an instance of
                pitest.TestCaseArgs.
        """

        scope = {}
        exec(source_code, scope)
        default_name = '__pitest_main_default_args_name__'
        if not default_name in scope:
            raise MainError('''Cannot find {} in source code, enclosed in ```:\n\n```\n{}\n```'''
                            .format(default_name, source_code))
        actual_args_name = args_name if args_name else scope[default_name]
        if not actual_args_name in scope:
            raise MainError("Name '{}' is not defined in source code."
                           .format(actual_args_name))
        obj = scope[actual_args_name]
        if not isinstance(obj, args.TestCaseArgs):
            raise MainError("Retrieved object, named '{}' is not an instance of pitest.TestCaseArgs"
                           .format(actual_args_name))

        return obj
