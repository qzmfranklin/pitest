import os
import pitest
import unittest

class CaseForTestArgs(pitest.TestCase):
    def test_foo(self, arg0, *, kwarg0):
        pass
    def test_bar(self, arg0, *, kwarg0):
        pass
    def setup(self, arg1, *, kwarg1):
        pass

class TestArgs(unittest.TestCase):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    test_dir = os.path.join(curr_dir, 'test_dir')
    testcase_class = CaseForTestArgs

    def test_args(self):
        args_obj = pitest.args.Args()
        args_obj.set_method_args('test', args = ('test arg0', ),
                kwargs = {'kwarg0': 'the value of kwarg0'})
        args_obj.set_method_args('setup', args = ('setup arg1', ),
                kwargs = {'kwarg1': 'the value of kwarg1'})

        args, kwargs = args_obj.get_method_args('__init__')
        instance = self.testcase_class(*args, **kwargs)
        args_obj.call_method(instance.setup_instance)
        for func in instance._get_all_tests():
            args_obj.call_method(instance.setup)
            args_obj.call_method(func[1])
            args_obj.call_method(instance.teardown)
        args_obj.call_method(instance.teardown_instance)

if __name__ == '__main__':
    unittest.main(verbosity = 0)
