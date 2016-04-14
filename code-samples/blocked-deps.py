#!/usr/bin/env python3

"""
Demonstrate how the PASS/FAIL information is conveyed.

Basic usage is found at basic-usage.py.

The test cases in this program has the following dependencies
( A -> B: A depends on B )
                   -> 4
                  /     \\
                 /       \\
        0 ---> 1 ---> 2 ---> 3

Each test case has two test methods, test_foo and test_bar. DemoCase2.bar and
DemoCase4.bar are programmed to fail while all other tests are programmed to
succeed.

There are two kinds of blocking:
    a)  Within a test case, a failed test method blocks other test methods.
        DemoCase2.bar blocks DemoCase2.foo due to _internal_deps (internal
        dependencies). Whereas DemoCase4.bar does not block DemoCase4.foo
        because there is no _internal_deps.
    b)  Acrodss test cases, a failed test case blocks other test cases.
        Both DemoCase2 and DemoCase4 fail. They directly block DemoCase1 and
        indirectly block DemoCase0. In the test result summary, DemoCase1 is
        BLOCKED and DemoCase0 is UNKNOWN.

Currently, there is no EXPECT or ASSERT like the usual unit test frameworks.
A test is considered as PASS if it does not return or returns None. The test is
considered FAIL if it returns anything else and the returned object is the error
information.
"""

import pitest

import os
import sys

class CaseBase(pitest.TestCase):
    def test_foo(self):
        pass
    def test_bar(self):
        pass

class TestSuiteDemo(pitest.TestSuiteBase):
    testcase_baseclasses = [ 'CaseBase' ]

class DemoCase0(CaseBase):
    deps = [ 'DemoCase1' ]
class DemoCase1(CaseBase):
    deps = [ 'DemoCase2', 'DemoCase4' ]
class DemoCase2(CaseBase):
    deps = [ 'DemoCase3' ]
    _internal_deps = { 'test_foo': [ 'test_bar' ] }
    def test_bar(self):
        return ' <--- PROGRAMMED TO FAIL, blocks DemoCase2.foo'
class DemoCase3(CaseBase):
    pass
class DemoCase4(CaseBase):
    deps = [ 'DemoCase3' ]
    def test_bar(self):
        return ' <--- PROGRAMMED TO FAIL, does not block DemoCase4.foo'

if __name__ == '__main__':
    print(__doc__)
    suite = TestSuiteDemo()
    suite.load_file(__file__)
    print('''\n
Here is what you would see when you print the result of the suite, enclosed
in ```:
\n
```
''')
    result = pitest.Runner.run_test_suite(suite)
    print(result)
    print('''```

DemoCase1 is BLOCKED whereas DemoCase0 is UNKNOWN. This is because DemoCase1 has
a failed prerequisite, DemoCase2, but none of DemoCase0's prerequisites failed.

Another reason for marking DemoCase0 as UNKNOWN is that it did not appear in the
test result at all.
''')
