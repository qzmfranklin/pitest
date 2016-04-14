import os
import pitest
import unittest

class FooClass(object):
    pass

class BarClass(object):
    def foo_method():
        pass
    def bar_method():
        pass

def foo_function(object):
    pass

def bar_function(object):
    pass

class SubGlobClass(object):
    def test_foo1():
        pass
    def test_foo2():
        pass
    def test_bar():
        pass

class TestName(unittest.TestCase):

    def test_property_name(self):
        paths = [
            '.usr.lib.python.unit_test',
            'relative.path.to.this_module',
            'foo.bar.',
            os.path.expanduser('~/tmp/foo').replace('/', '.').replace('-', '_'),
        ]
        objs = [ FooClass, BarClass, foo_function, bar_function ]
        for path in paths:
            for obj in objs:
                name_obj = pitest.PyName(path, obj)
                expected_name = path.rstrip('.') + '.' + obj.__name__
                actual_name = name_obj.name
                self.assertEqual(expected_name, actual_name)

    def test_sub(self):
        paths = [
            ('foo.bar', 'foo.bar'),
            ('foo.bar.', 'foo.bar'),
            ('', ''),
            ('.', ''),
        ]
        for path, subpath in paths:
            name_obj = pitest.PyName(path, BarClass)
            for method_name in ['foo_method', 'bar_method']:
                expected_name = '{}.{}.{}'.format(subpath,
                                    BarClass.__name__, method_name)
                actual_name = name_obj.sub(method_name).name
                self.assertEqual(expected_name, actual_name)
            # Non-existing attributes is subbed to None.
            for method_name in ['no way', 'foo_method2']:
                self.assertEqual(None, name_obj.sub(method_name))

    def test_subglob(self):
        path = 'foo.bar'
        test_nos = pitest.PyName(path, SubGlobClass).subglob('test_foo*')
        expected = {
            '{}.SubGlobClass.test_foo1'.format(path),
            '{}.SubGlobClass.test_foo2'.format(path),
        }
        actual = set([no.name for no in test_nos])
        self.assertEqual(actual, expected)

    def test_to_pyname(self):
        expect_true_samples = [
                ('path/to/unittest.py', 'path.to.unittest'),
                ('/path/to/unittest.py', '.path.to.unittest'),
                ('/path/to/unit-test.py', '.path.to.unit_test'),
                ('~/git/pylib.py', os.path.expanduser('~').replace('/',
                    '.').replace('-', '_') + '.git.pylib'),
        ]
        expect_error_samples = [
                'usr/foo.bar', # does not end with '.py'
                'some.path/foo.bar.py', # has dot
                'colon:is/prohibited.py', # has colon
        ]
        for fname, pname, in expect_true_samples:
            self.assertEqual(pitest.PyName.to_pyname(fname), pname)
        for fname in expect_error_samples:
            with self.assertRaises(pitest.name.PyNameError):
                pitest.PyName.to_pyname(fname)

    def test_glob_match(self):
        expect_true_samples = [
                ('bar.Case1', [ 'Case1' ]),
                ('foo.bar.Case2', [ 'Case2', 'bar.Case2', 'foo.bar.Case2' ]),
        ]
        expect_false_samples = [
                ('foo.bar.Case1', [ 'foo.Case1', '.Case1', 'Case2', 'ase1' ]),
                ('foo.bar.Case100', [ 'foo.Case1', 'Case10', '.Case100' ]),
        ]
        for haystack, needles in expect_true_samples:
            for needle in needles:
                self.assertTrue(pitest.PyName.glob_match(haystack, needle))
        for haystack, needles in expect_false_samples:
            for needle in needles:
                self.assertFalse(pitest.PyName.glob_match(haystack, needle))

    def test_glob_match_glob(self):
        expect_true_samples = [
                ('foo.bar.Case1', ['Case*', 'bar.Case*', 'ba*.Case1', 'ba*.Cas*']),
        ]
        expect_false_samples = [
                ('foo.bar.Case1', ['Case*2', 'bar.Case', 'b*.Case']),
        ]
        for haystack, needles in expect_true_samples:
            for needle in needles:
                self.assertTrue(pitest.PyName.glob_match(haystack, needle))
        for haystack, needles in expect_false_samples:
            for needle in needles:
                self.assertFalse(pitest.PyName.glob_match(haystack, needle))

if __name__ == '__main__':
    unittest.main(verbosity = 0)
