======
pitest
======

.. image:: https://travis-ci.org/qzmfranklin/pitest.svg?branch=master
    :target: https://travis-ci.org/qzmfranklin/pitest
    :alt: Build status

An object oriented testing framework.


Installation
============

From pip3::

    $ pip3 install --upgrade pitest

From source::

    $ python3 setup.py --quiet install

Tests
=====

Install the pitest package first, then::

    $ cd unittests
    $ python3 -m unittest

Usage Examples
=======================

1. Write a test case:

.. code-block:: python

    import pitest

    class MyTestCase(pitest.TestCaseBase):
        # By default, test methods are methods whose names start with 'test_'. You
        # can change the matching patterns by defining the 'test_patterns' class
        # variable by uncommenting the following line:
        #       test_patterns = [ 'mytest_*', 'yourtest_*' ]

        # The start * means it matches anything, just like the command line glob.

        # If test methods have inter-dependencies, i.e., certain tests must precede
        # some other tests, you can define the dependencies using the
        # 'internal_deps' class variable. Here is an example:
        #       internal_deps = { 'test_foo1': [ 'test_bar1*', 'test_bar2*' ],
        #                         'test_hel*lo': [ 'test_no', 'test_yes*' ],
        #                       }

        # If this test case depend on other test cases, you can specify their
        # dependencies via the 'deps' class variable. Here is an example:
        #       deps = [ 'MyTestCase1', 'MyTestCaseFoo*', ]

        # When you reference other test cases, you do NOT need to import the files
        # that define the referenced test cases. But if they cannot be found by the
        # end of the day, error will occur.

        def __init__(self[, *args[, **kwargs]]):
            pass

        # Run once before running all test methods.
        def setup_instance(self[, *args[, **kwargs]]):
            pass

        # Run once after running all test methods.
        def teardown_instance(self[, *args[, **kwargs]]):
            pass

        # Run once before running every single test method.
        def setup(self[, *args[, **kwargs]]):
            pass

        # Run once after running every single test method.
        def teardown(self[, *args[, **kwargs]]):
            pass

        # Actual test methods, names matching 'test_patterns'.
        def test_foo_something(self[, *args[, **kwargs]]):
            pass
        def test_foo_something_else(self[, *args[, **kwargs]]):
            pass
        def test_bar_something(self[, *args[, **kwargs]]):
            pass
        def test_bar_something_else(self[, *args[, **kwargs]]):
            pass

2. Write argument file

.. code-block:: python

    import pitest

    __pitest_main_default_args_name__ = 'my_args'

    my_args = pitest.Args()
    my_args.set_method_args('__init__',
            args = ('Anndee', ),
            kwargs = { 'kwarg0': 'KoolArg' })
    my_args.set_method_args('test',
            args = ('naathing', ),
            kwargs = { 'kwarg1': 'at owl' })

    my_args2 = pitest.Args()
    my_args2.set_method_args('__init__',
            args = ('Bashii', ),
            kwargs = { 'kwarg0': 'KoolArg2' })
    my_args2.set_method_args('test',
            args = ('naathing', ),
            kwargs = { 'kwarg1': 'at owlll' })

3. Run the test cases

Discover tests::

    $ python3 -m pitest discover (case | method | all)

Run tests::

    $ python3 -m pitest run (case | method) name

Scan given directory::

    $ python3 -m pitest --start-dir some/dir ...

Run tests with dynamic arguments::

    $ python3 -m pitest run case MyTestCase --args-file my_args.py

Use a non-default argument object in the file::

    $ python3 -m pitest run case MyTestCase --args-file my_args.py \
                                            --args-name my_args2
