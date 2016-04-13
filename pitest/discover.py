from . import case

import fnmatch
import glob
import inspect
import os
import re
import sys

class DiscoverError(Exception):
    pass

class Discover:

    @staticmethod
    def discover(start_dir, *, baseclasses = [ case.TestCase.__name__ ],
            recursive = True, pattern = '*.py'):
        """Discover test cases.

        Scan @start_dir directory recursively for files whose name match
        @pattern. Load test cases, if any, from matched files.

        Discovered test cases use directory hierarchy to construct their unique
        IDs. Test cases with the same class name but reside in different source
        files are considered as distinct test cases.

        For example:
            foo.py: class UnitTest
            bar.py: class UnitTest
        When loaded, they have names:
            foo.UnitTest
            bar.UnitTest

        When you specify dependencies among test cases using TestCase.deps,
        you can choose to only specify the class name. If there is only one
        matching class loaded, that class is referenced. If more than one loaded
        class has that class name, the get_deps_graph() program will raise
        error.

        For example:
            given:
                foo.py: class UnitTest: pass
                bar.py: class UnitTest: pass
            good:
                class Case1(pitest.TestcaseBase):
                    deps = [ 'foo.UnitTest', 'bar.UnitTest' ]
            bad: cannot resolve between foo.unittest and bar.unittest
                class Case1(pitest.TestcaseBase):
                    deps = [ 'UnitTest' ]

        Args:
            return: A list of classes.
            baseclasses: A list of names of test case base classes. Only
                subclasses of at least one class in this list are loaded.
            recursive: True:  Recursively scan all subdirectories of @start_dir.
                False: Only scan files in @start_dir.

        Raises:
            DiscoverError: start_dir is not a directory.
        """
        if not os.path.isdir(start_dir):
            raise DiscoverError('start_dir {} is not a directory'.format(start_dir))

        testcases = []
        if recursive:
            reg_pattern = fnmatch.translate(pattern)
            for root, dirs, files in os.walk(start_dir):
                for fname in [ f for f in files if re.match(reg_pattern, f) ]:
                    fullpath = os.path.join(root, fname)
                    relpath = os.path.relpath(fullpath)
                    testcases += Discover.load_file(relpath,
                            baseclasses = baseclasses)
        else:
            file_list = glob.glob(start_dir + '/' + pattern)
            for fname in file_list:
                testcases += Discover.load_file(fname, baseclasses = baseclasses)
        return testcases


    @staticmethod
    def load_file(fname, *, baseclasses = [ case.TestCase.__name__ ]):
        """Load test cases from a single file.

        Namespace rules applies the same way as documented in discover().

        Returns:
            A list of (full_cls_name, cls) tuples.
            A full_cls name looks like this:
                .some.path.to.this_module.some_class
            The full_cls_name introduces namespaces to test discovery.

        Args:
            baseclasses: A list of names of test case base classes. Only
                subclasses of at least one class in this list are loaded.
        """

        realpath    = os.path.realpath(fname)
        dirname     = os.path.dirname(realpath)
        basename    = os.path.basename(realpath)
        module_name = os.path.splitext(basename)[0]

        sys.path.append(dirname)
        module = __import__(module_name, globals())
        sys.path.pop()

        classes_map = inspect.getmembers(module, inspect.isclass)
        classes = []
        for cls_name, cls in classes_map:
            for super_cls in inspect.getmro(cls)[1:]:
                full_super_cls_name = Discover._convert_path(fname) + '.' + super_cls.__name__
                if Discover._match_full_class_name(full_super_cls_name, baseclasses):
                    full_cls_name = Discover._convert_path(fname) + '.' + cls_name
                    cls_tuple = (full_cls_name, cls)
                    classes.append(cls_tuple)

        return classes

    @staticmethod
    def _match_full_class_name(full_cls_name, baseclasses):
        """Check if a full class name matches any in a given list.

        This method does not require the baseclass to be loaded to function.
        No glob patterns allowed.

        Returns:
            True: If at least one of baseclasses matches full_cls_name.
            False: Otherwise

            For example:
                ('foo.bar.Case1', 'Case1')          => True
                ('foo.bar.Case1', 'bar.Case1')      => True
                ('foo.bar.Case1', 'foo.Case1')      => False
                ('foo.bar.Case1', 'Case2')          => False
                ('foo.bar.Case100', 'Case10')       => False

        Args:
            full_cls_name: The class object to test.
            baseclasses: A list of names of base classes.
        """
        for baseclass in baseclasses:
            reg_pattern = '^(({0})|(.*\.{0}))$'.format(baseclass)
            if re.match(reg_pattern, full_cls_name):
                return True
        return False

    @staticmethod
    def _convert_path(fname):
        """Convert UNIX path to python package name.

        Example:
            /usr/lib/python/unit-test.py      =>    .usr.lib.python.unit_test
            relative/path/to/this_modue.py    =>    relative.path.to.this_module

        Expand '~' to $HOME.
        Does not resolve symlinks or absolute path.
        Replace hypen '-' with underscore '_'.

        Raises:
            DiscoverError: The file name contains dot '.'.
        """
        basename, ext = os.path.splitext(os.path.expanduser(os.path.normpath(fname)))
        if ext != '.py':
            raise DiscoverError("Path '{}' must be a python file, i.e, ends with '.py'.".format(fname))
        basename = basename.replace('-', '_')
        if len(set('.') & set(basename)) > 0:
            raise DiscoverError("Path '{}' must not have '.'.".format(basename))
        retval = basename.replace('/', '.')
        return retval
