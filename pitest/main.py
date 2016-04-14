from . import args

import argparse
import fnmatch
import re

class MainError(Exception):
    pass

class Main(object):
    """Helper class for __main__.py

    Functions in this class are useful for creating driver scripts.
    """

    @staticmethod
    def update_parser(parser):
        """Get a parser for parsing pitest-related argument.

        Returns:
            An argparse.ArgumentParser object.
        """

        gp = parser.add_argument_group('test options')
        gp.add_argument('--basecases',
            metavar = 'CLASS',
            nargs = '+',
            default = [ 'TestCaseBase' ],
            help = 'base test case classes to discover')
        gp.add_argument('--start-dir',
            metavar = 'DIR',
            default = '.',
            help = 'start directory for recursive scan')
        gp.add_argument('-R', '--recursive',
            action = 'store_true',
            help = 'recursively scan the start-dir')
        gp.add_argument('--file-pattern',
            metavar = 'PATTERN',
            default = '*.py',
            help = 'pattern of files to scan')
        gp.add_argument('--no-deps-tracking',
            action = 'store_true',
            help = 'do not track dependencies')

        subparsers = parser.add_subparsers(dest = 'command')

        sp = subparsers.add_parser('discover',
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            help = 'list discovered test cases and test methods')

        sp = subparsers.add_parser('run',
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            help = 'run test method(s)')
        sp.add_argument('test',
            metavar = 'TEST',
            type = str,
            nargs = '*',
            help = '''list of test methods to run, None = run
                        all discovered tests''')

        gp = sp.add_argument_group('args')
        gp.add_argument('--args-file',
            metavar = 'FILE',
            type = str,
            help = '''python3 source file that defines the args_obj,
                    None = empty argument''')
        gp.add_argument('--args-name',
            metavar = 'NAME',
            default = 'PITEST_ARGS',
            help = 'name of the Args object in the source code')

        return parser

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
            A instance of pitest.Args.

        Args:
            source_code: python3 code that defines the args object. The source
                code can define one or more args objects. The source code must
                define a string object named '__pitest_main_default_args_name__'
                and define an pitest.Args object whose name is the value
                of __pitest_main_default_args_name__.
            args_name: A string, the name of the pitest.Args object to
                return. Override the one specified by
                __pitest_main_default_args_name__ in the source code.
                None = do not override __pitest_main_default_args_name__.

        Raises:
            Whatever exceptions exec(source_code) raises.
            MainError: If __pitest_main_default_args_name__ is not defined in
                source code, or if the source code does not define object with
                the given name, or if the retrieved object is not an instance of
                pitest.Args.
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
        if not isinstance(obj, args.Args):
            raise MainError("Retrieved object, named '{}' is not an instance of pitest.Args"
                           .format(actual_args_name))

        return obj
