#!/usr/bin/env python3

import pitest

import argparse
import inspect
import os
import re
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        description = 'pitest main script')

    parser.add_argument('--start-dir', type = str,
        default = '.',
        help = 'start directory for recursive scan')
    parser.add_argument('--basecases', type = str,
        nargs = '+',
        default = [ 'TestCase' ],
        help = 'base test case classes to discover')
    parser.add_argument('--recursive', action = 'store_true',
        default = False,
        help = 'recursively scan the start-dir')
    parser.add_argument('--file-pattern', type = str,
        default = '*.py',
        help = 'pattern of files to scan')

    subparsers = parser.add_subparsers(dest = 'command')

    sp = subparsers.add_parser('discover',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    sp.add_argument('discover_kind', metavar = 'KIND',
        type = str,
        choices = ['all', 'case', 'method'],
        help = 'what to discover, one of [ all, case, method ]')

    sp = subparsers.add_parser('run',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        description = 'Can only run tests that do not take any arguments.')
    sp.add_argument('run_kind', metavar = 'KIND',
        type = str,
        choices = ['case', 'method'],
        help = 'what kind of target to run, one of [ case, method ]')
    sp.add_argument('run_target_name', metavar = 'TARGET',
        type = str,
        #nargs = '+',
        help = 'name of the target to run')
    sp.add_argument('--args-file',
        default = None,
        help = '''python3 source file that defines the args_obj.
                None = no arguments.''')
    sp.add_argument('--args-name',
        default = None,
        help = '''name of the Args object in the source code. This
                    argument is used to override the default name defined in
                    __pitest_main_default_args_name__ in the source code.
                    None = use default, i.e., the one defined by
                    __pitest_main_default_args_name__.''')

    args = parser.parse_args()

    if args.command in ['discover', 'run']:
        testcases = pitest.Discover.discover(
            args.start_dir,
            baseclasses = args.basecases,
            recursive = args.recursive,
            pattern = args.file_pattern
        )

    if args.command == 'discover':
        if args.discover_kind == 'case':
            for full_cls_name, cls in testcases:
                print(full_cls_name)
        elif args.discover_kind == 'method':
            for full_cls_name, cls in testcases:
                for method_name, method in cls._get_all_tests_class():
                    print('{}.{}'.format(full_cls_name, method_name))
        elif args.discover_kind == 'all':
            for full_cls_name, cls in testcases:
                print(full_cls_name)
                for method_name, method in cls._get_all_tests_class():
                    print('{}.{}'.format(full_cls_name, method_name))

    elif args.command == 'run':
        # Create an Args object.
        args_obj = None
        init_args, init_kwargs = ((), {})
        if args.args_file:
            with open(args.args_file, 'r', encoding = 'utf8') as f:
                args_obj = pitest.Main.get_args_obj_from_source_code(
                    f.read(), args_name = args.args_name)
            init_args, init_kwargs = args_obj.get_method_args('__init__')
        if args.run_kind == 'case':
            testcases_to_run = pitest.Main.find_all_test_cases_by_name(
                args.run_target_name, testcases)
            for full_cls_name, cls in testcases_to_run:
                cls_instance = cls(*init_args, **init_kwargs)
                result = pitest.Runner.run_test_case(
                    cls_instance,
                    args_obj,
                    fullname = full_cls_name,
                )
                print(result)
        elif args.run_kind == 'method':
            test_args, test_kwargs = args_obj.get_method_args('test') if args_obj else ((), {})

            target_cls_name, target_method_name = os.path.splitext(args.run_target_name)
            full_reg_pattern = '^({0})|(.*\.{0})$'.format(args.run_target_name)
            full_reg_engine = re.compile(full_reg_pattern)
            cls_reg_pattern = '^({0})|(.*\.{0})$'.format(target_cls_name)
            cls_reg_engine = re.compile(cls_reg_pattern)
            # os.path.splitext('.method_name') => ('.method_name', '')
            if not target_method_name:
                # '.method_name' or 'method_name', brute force search.
                for full_cls_name, cls in testcases:
                    for method_name, cls_method in cls._get_all_tests_class():
                        full_method_name = full_cls_name + '.' + method_name
                        if not full_reg_engine.match(full_method_name):
                            continue
                        # Instantiate the class, call the test method.
                        cls_instance = cls(*init_args, **init_kwargs)
                        info = inspect.getmembers(cls_instance, inspect.ismethod)
                        for name, method in info:
                            ful_name = full_cls_name + '.' + name
                            if full_reg_engine.match(ful_name):
                                method(*test_args, **test_kwargs)
                        break
            else:
                # '.partial_cls_name.method_name', match the class name first.
                for full_cls_name, cls in testcases:
                    if not cls_reg_engine.match(full_cls_name):
                        continue
                    for method_name, cls_method in cls._get_all_tests_class():
                        full_method_name = full_cls_name + '.' + method_name
                        if not full_reg_engine.match(full_method_name):
                            continue
                        # Instantiate the class, call the test method.
                        cls_instance = cls(*init_args, **init_kwargs)
                        info = inspect.getmembers(cls_instance, inspect.ismethod)
                        for name, method in info:
                            ful_name = full_cls_name + '.' + name
                            if full_reg_engine.match(ful_name):
                                method(*test_args, **test_kwargs)
                        break
