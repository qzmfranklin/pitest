from . import case
from . import name

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
    def discover(start_dir, *, recursive = True, pattern = '*.py',
                 baseclass = case.TestCase.__name__):
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

        Returns:
            A list of pitest.PyName objects, whose name property is the full
            name of the test case class, and the obj attribute is the test case
            class object.

        Args:
            return: A list of classes.
            baseclass: A list of names of test case base classes. Only
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
                for fname in files:
                    if re.match(reg_pattern, fname):
                        fullpath = os.path.join(root, fname)
                        testcases += Discover.load_file(fullpath,
                                basepath = start_dir, baseclass = baseclass)
        else:
            glob_pattern = os.path.join(start_dir, pattern)
            for fname in glob.glob(glob_pattern):
                testcases += Discover.load_file(fname,
                        basepath = start_dir, baseclass = baseclass)
        return testcases

    @staticmethod
    def load_file(fname, *, baseclass = case.TestCase.__name__,
            basepath = None, resolve_symlink = False):
        """Load test cases from a single file.

        Namespace rules applies the same way as documented in discover().

        Returns:
            A list of pitest.PyName objects.

        Args:
            fname: The file to load.
            baseclass: A list of names of test case base classes. Only
                subclasses of at least one class in this list are loaded.
            basepath: The base path to compute relative path with. The default,
                None, means use os.getcwd().
            resolve_symlink: Boolean. True = resolve symlinks in fname. False
                otherwise.
        """
        # Compute name_prefix.
        basepath    = basepath if basepath else os.getcwd()
        if resolve_symlink:
            fullpath = os.path.realpath(fname)
            basepath = os.path.realpath(basepath)
        else:
            fullpath = os.path.abspath(fname)
        relpath     = os.path.relpath(fullpath, basepath)
        name_prefix = name.PyName.to_pyname(os.path.normpath(relpath))

        # __import__ the module.
        dirname     = os.path.dirname(fullpath)
        basename    = os.path.basename(fullpath)
        module_name = os.path.splitext(basename)[0]
        sys.path.append(dirname)
        module = __import__(module_name, globals())
        sys.path.pop()

        # Get subclasses of baseclass.
        classes_map = inspect.getmembers(module, inspect.isclass)
        classes = []
        for cls_name, cls in classes_map:
            for super_cls in inspect.getmro(cls)[1:]:
                # The trailing 'no' stands for 'name object'.
                super_cls_no = name.PyName(name_prefix, super_cls)
                if super_cls_no.match(baseclass):
                    cls_no = name.PyName(name_prefix, cls)
                    classes.append(cls_no)

        return classes
