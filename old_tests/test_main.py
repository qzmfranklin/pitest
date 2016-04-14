import pitest

import os
import subprocess
import unittest

class TestMain(unittest.TestCase):
    old_cwd = None

    @classmethod
    def setUpClass(cls):
        cls.old_cwd = os.getcwd()
        this_dir = os.path.dirname(os.path.realpath(__file__))
        curr_dir = os.path.join(this_dir, '../..')
        os.chdir(curr_dir)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.old_cwd)

    def test_run_case_default_arg(self):
        cmdstr = '''\
python3 -m pitest \\
            --start-dir pitest/unittests/test_main_dir \\
            run case test_main_dir.cases.Case3 \\
            --args-file pitest/unittests/test_main_dir/args1.py
'''
        actual = subprocess.check_output(cmdstr, shell = True).decode('utf8')
        expected = '''\
Case3.__init__(Anndee, kwarg0 = KoolArg)
Case3.test_foo(naathing, kwarg1 = at owl)
pitest.unittests.test_main_dir.cases.Case3: finished 1 tests

'''
        self.assertEqual(actual, expected)

    def test_run_case_nondefault_arg(self):
        cmdstr = '''\
python3 -m pitest \\
            --start-dir pitest/unittests/test_main_dir \\
            run case test_main_dir.cases.Case3 \\
            --args-file pitest/unittests/test_main_dir/args1.py \\
            --args-name my_args2
'''
        actual = subprocess.check_output(cmdstr, shell = True).decode('utf8')
        expected = '''\
Case3.__init__(Bashii, kwarg0 = KoolArg2)
Case3.test_foo(naathing, kwarg1 = at owlll)
pitest.unittests.test_main_dir.cases.Case3: finished 1 tests

'''
        self.assertEqual(actual, expected)

    def test_run_method_default_arg(self):
        cmdstr = '''\
python3 -m pitest \\
            --start-dir pitest/unittests/test_main_dir \\
            run method cases.Case4.test_bar \\
            --args-file pitest/unittests/test_main_dir/args1.py
'''
        actual = subprocess.check_output(cmdstr, shell = True).decode('utf8')
        expected = '''\
Case4.__init__(Anndee, kwarg0 = KoolArg)
Case4.test_bar(naathing, kwarg1 = at owl)  <===  Only Case4 has test_bar()
'''
        self.assertEqual(actual, expected)

    def test_run_method_only_method_name(self):
        cmdstr = '''\
python3 -m pitest \\
            --start-dir pitest/unittests/test_main_dir \\
            run method test_bar \\
            --args-file pitest/unittests/test_main_dir/args1.py \\
            --args-name my_args2

'''
        actual = subprocess.check_output(cmdstr, shell = True).decode('utf8')
        expected = '''\
Case4.__init__(Bashii, kwarg0 = KoolArg2)
Case4.test_bar(naathing, kwarg1 = at owlll)  <===  Only Case4 has test_bar()
'''
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
