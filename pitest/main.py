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
