import os
import re

class PyNameError(Exception):
    pass

class PyName(object):
    """Provide python name service to other classes and methods.

    Utilities for managing python style names for objects:
        - to_pyname: Convert python file names to python style paths.
        - sub: Create a new PyName object from an attribute of this object.
        - re_match, match: Match python style names.
    """

    def __init__(self, prefix, obj):
        """
        Arguments
            prefix: A python style module name. Trailing dots are trimed.
            obj: The object to service. Must have the __name__ attribute.
        """
        self._prefix = prefix.rstrip('.')
        self._obj = obj

    @property
    def name(self):
        """Full python style name of the object."""
        return '{}.{}'.format(self._prefix, self._obj.__name__)

    @staticmethod
    def re_match(haystack, needle):
        """Is needle at the end of the haystack.

        Returns:
            True if it is a match. False otherwise.

        For example, for the following (self.name, name) tuples:
            ('foo.bar.Case1', 'Case1')          => True
            ('foo.bar.Case1', 'bar.Case1')      => True
            ('foo.bar.Case1', 'foo.Case1')      => False
            ('foo.bar.Case1', 'Case2')          => False
            ('foo.bar.Case100', 'Case10')       => False
        """
        reg_pattern = '^(({0})|(.*\.{0}))$'.format(needle)
        return re.match(reg_pattern, haystack)

    def match(self, name):
        """Match self.name to the given name."""
        return PyName.re_match(self.name, name)

    def sub(self, attribute):
        """Get a new PyName object from attribute.

        Returns:
            The new PyName object, constructed using (self.name, attribute). If
            the object serviced by self, i.e, self._obj, does not have that
            attribute, return None.

        Arguments:
            attribute: The attribute to get.
        """
        if hasattr(self._obj, attribute):
            obj = getattr(self._obj, attribute)
            return PyName(self.name, obj)
        else:
            return None

    @staticmethod
    def to_pyname(fname):
        """Convert UNIX path to python style name.

        Example:
            /usr/lib/python/unit-test.py      =>    .usr.lib.python.unit_test
            relative/path/to/this_modue.py    =>    relative.path.to.this_module

        Expand '~' to $HOME.
        Does not resolve symlinks or absolute path.
        Replace hypen '-' with underscore '_'.

        Raises:
            PyNameError: The file name contains dot '.' or the colon ':', or the
                file is not a python file, i.e, does not end with .py.
        """
        basename, ext = os.path.splitext(
            os.path.expanduser(os.path.normpath(fname)))
        if ext != '.py':
            raise PyNameError("Path must be a python file: '{}'".format(fname))
        basename = basename.replace('-', '_')
        if len(set('.:') & set(basename)) > 0:
            raise PyNameError("Path '{}' must not have dot '.' or ':'.".format(basename))
        retval = basename.replace('/', '.')
        return retval
