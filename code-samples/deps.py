#!/usr/bin/env python3

"""
Demonstrate how to track dependencies using pitest.

This program is a standalone program that can run from any directory as long as
env.dev is sourced.

In-source comments provide information on how to modify parts of the code to do
things that are demonstrated, on any recommended usage, and/or about the more
complete listing of a partialy demonstrated feature.

In this sample, each test case only has one test method that prints the name of
the test case and the argument list.

The test cases have the following dependencies:
( A -> B: A depends on B )

         8      10
           \      \\
            \      \\
             \      \\
  7 ---> 0 ---> 1 ---> 3 ---> 4
   \       \        /
    \       \      /
     \       \    /
      -> 9 ---> 2

Because of namespace, this program yields different output when run from
different working directories.
"""

import pitest

import os
import sys

# To save some coding, the setup() and test_foo() methods are implemented in the
# base test case class, CaseBase. DemoCase3 implements a test_bar().
class CaseBase(pitest.TestCase):
    def setup(self):
        pass
    def test_foo(self):
        print("Running {}.test_foo".format(self.__class__.__name__))

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
#   When specifying the deps, you can reference test cases by partial names. If
#   there is no other loaded test cases that match '*bar.TestCase0',
#   'bar.TestCase0' resolves uniquely to 'foo.bar.TestCase0'. Otherwise, pitest
#   will raise error complaining about adding the same class twice.
#
# To save some coding, the setup() and test_foo() methods are implemented in the
# base test case class, CaseBase. DemoCase3 implements a test_bar().
class DemoCase0(CaseBase):
    # You can reference a test case by either the full name, or part of the full
    # name.
    deps = [ 'deps.DemoCase1', 'DemoCase2' ]
class DemoCase1(CaseBase):
    deps = [ 'DemoCase3' ]
class DemoCase2(CaseBase):
    deps = [ 'DemoCase3' ]
class DemoCase3(CaseBase):
    deps = [ 'DemoCase4' ]
    def test_bar(self):
        print("Running {}.test_bar <-- Only DemoCase3 has test_bar()"
                .format(self.__class__.__name__))
class DemoCase4(CaseBase):
    # This test case does not depend on any other test cases. Therefore it will
    # be the first test case to run.
    pass
class DemoCase7(CaseBase):
    deps = [ 'DemoCase0', 'DemoCase9' ]
class DemoCase8(CaseBase):
    deps = [ 'DemoCase1' ]
class DemoCase9(CaseBase):
    deps = [ 'DemoCase2' ]
class DemoCase10(CaseBase):
    deps = [ 'DemoCase3' ]

if __name__ == '__main__':
    print(__doc__)

    suite = TestSuiteDemo()
    suite.load_file(__file__)

    print('''\n
When the program runs, it prints stuff like this, enclosed in ```:
\n
```''')
    # Run the test suite with the args_obj.
    result = pitest.Runner.run_test_suite(suite)
    print('''```\n
Note that:
    a)  The test cases are run in a order that does not violate the dependency
        graph.
    b)  DemoCase0 prints setup() because it implements a setup() method that
        prints stuff.
''')

    # Print the test result.
    print('''\n
Here is the summary of test result you would see if you print the test result,
enclosed in ```:

```''')
    print(result)
    print('```')
