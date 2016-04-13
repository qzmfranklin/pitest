#!/usr/bin/env python3

"""
Demonstrate passing arguments and report PASS/FAIL.

This program is a standalone program that can run from any directory as long as
env.dev is sourced.

PASS/FAIL:
    This program defines several test cases and run them. Each test case has two
    test methods. One of the test cases if programmed to fail. Others, though,
    will continue to run. Summary of the test is printed at the end of the
    program.

Test Naming:
    Test methods in this program are universally named test_foo and test_bar. It
    does not mean test_foo and test_bar are the only valid names for test
    methods.  Anything test starting with 'test_' is picked up by pitest. You
    can change the name matching pattern by modifying
    pitest.TestCaseBase.test_patterns when you derive a new base test case
    class.
"""

import pitest

import os
import sys

# Use a custom base test case to define the arguments.
# This is not mandatory but highly recommended. The reasons are:
#    -  You can use this base test case class to declare the interface of your
#       test cases in just 'one place'.
#    -  When creating a test suite, you can specify your test suite to only
#       discover test cases that are subclasses of this base test case class.
#       This prevents loading test cases that have incompatible argument lists.
class CaseBase(pitest.TestCaseBase):
    def setup(self, arg0, arg1, arg2, *, kwarg, kool_arg):
        print('Running {}.setup() with {}, {}, {}, {}, {}'.format(
            self.__class__.__name__, arg0, arg1, arg2, kwarg, kool_arg))
    def test_foo(self, arg1, *, kwarg1):
        print('Running {}.test_foo() with {}, {}'.format(
            self.__class__.__name__, arg1, kwarg1))
    def test_bar(self, arg1, *, kwarg1):
        print('Running {}.test_bar() with {}, {}'.format(
            self.__class__.__name__, arg1, kwarg1))
    def teardown_instance(self, arg0, arg1):
        print('Running {}.teardown_instance() with {}, {}'.format(
            self.__class__.__name__, arg0, arg1))

# Define a test suite that only loads the custom test cases.
# If you omit testcase_baseclasses, all subclasses of pitest.TestCaseBase will
# be discovered and loaded when you call suite.discover() or suite.load_file().
class TestSuiteDemo(pitest.TestSuiteBase):
    testcase_baseclasses = [ 'CaseBase' ]

# Define test cases.
# All test cases must have exactly the same signature as defined by the base
# test case class (CaseBase).
#
# Namespace:
#   The directory hierarchy of files form the natural namespaces. The pitest
#   library internally uses namesapces constructed from the directory hierarchy
#   to uniquely identify test cases.
#
#   An example of the full name of a loaded test case:
#       foo.bar.TestCase0
#
#   Namespace is used to avoid naming conflicts. If your tests do not have
#   dependencies, you do not need to know anything about it as everything is
#   taken care of under the hood. However, if you want to use the dependency
#   tracking feature of pitest, you need to be aware of how names are resolved
#   and what would happen if there are conflicts. A good example of that is
#   deps.py.
#
# PASS/FAIL:
#     This program defines several test cases and run them. Each test case has
#     two test methods. DemoCase3.test_foo() if programmed to fail. All other
#     test cases, though, will continue to run and complete successfully.
#
#     To save some coding, the test_foo() and test_bar() methods are put in the
#     base test case class, CaseBase. DemoCase3.test_foo() implements its own
#     test_foo() and makes it fail.
class DemoCase0(CaseBase):
    pass
class DemoCase1(CaseBase):
    pass
class DemoCase2(CaseBase):
    pass
class DemoCase3(CaseBase):
    def test_foo(self, arg1, *, kwarg1):
        print('Running {}.test_foo() with {}, {} <--- PROGRAMMED TO FAIL'.format(
            self.__class__.__name__, arg1, kwarg1))
        return ' <--- PROGRAMMED TO FAIL'
class DemoCase4(CaseBase):
    pass
class DemoCase5(CaseBase):
    pass

if __name__ == '__main__':
    print(__doc__)

    # Create the argument object to pass into the test suite.
    #
    # The set of valid method names is:
    #   { '__init__', 'test', 'setup', 'teardown', 'setup_instance',
    #   'teardown_instance' },
    # though we only demo the usage with 'setup', 'teardown_instance', and
    # 'test'.
    #
    # You can provide arbitrary positional and keyword arguments to any number
    # of the above six methods in any way you want. The arguments passed to
    # different methods are independent of each other.
    # 
    # When using set_method_args, positional and keyword arguments are passed
    # through the 'args' keyword as a tuple and 'kwargs' keyword as a
    # dictionary, respectively.
    #
    # These arguments used here are just printed to stdout in this tutorial. But
    # you can freely use them inside your own test cases and test methods.
    #
    # If you tests do not take any arguments, you can completely skip the
    # creation of the args_obj object. When you call Runner.run_test_suite(),
    # just omit the second argument, args_obj. It defaults to no arguments.
    #
    # GOTCHA:
    #   ('arg') evaluates to 'arg', not a tuple. If you want a tuple with only
    #   one element, use ('arg', ).
    args_obj = pitest.Args()
    args_obj.set_method_args('setup',
            args = ('arbitrary_arg here', 'Keven', 'Amdy'),
            kwargs = {'kwarg': 'some value', 'kool_arg': 'deadbeaf'})
    args_obj.set_method_args('teardown_instance',
            args = ('simple', 'complext'))
    args_obj.set_method_args('test',
            args = ('arg1', ),
            kwargs = {'kwarg1': 'test kwarg'})

    # Create test suite, load file.
    suite = TestSuiteDemo()
    suite.load_file(__file__)
    # You can, alternatively, use suite.discover() to recursively scan a
    # directories and load all test cases there. Comment the load_file() line
    # above and uncomment the following line.
    # suite.discover('.')

    print('''\n
When the program runs, it prints stuff like this, enclosed in ```:
\n
```''')
    # Run the test suite with the args_obj.
    # If your test suite does not need to take any arguments, you can omit the
    # args_obj argument. It defaults to no arguments.
    result = pitest.Runner.run_test_suite(suite, args_obj)
    print('''```\n
Note that:
    a)  The test cases are run in a order that does not violate the dependency
        graph.
    b)  DemoCase0 prints setup() because it implements a setup() method that
        prints stuff.
    c)  teardown_instance() is invoked once per test case, setup() is invoked
        once per test method.
''')

    # Print the test result.
    print('''\n
Here is the summary of test result you would see if you print the test result,
enclosed in ```:

```''')
    print(result)
    print('```')
