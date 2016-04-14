import os
import pitest
import unittest

class TestCaseResult(unittest.TestCase):
    case_result = None

    def setUp(self):
        self.case_result = pitest.TestCaseResult('CaseClass')
        for i in range(4):
            self.case_result.add_success('test{}'.format(i))

    def test_success(self):
        result = self.case_result
        self.assertTrue(result.success)
        expected_result_string = 'CaseClass: finished 4 tests\n'
        self.assertEqual(str(result), expected_result_string)

    def test_failure(self):
        result = self.case_result
        result.add_failure('test10', 'failed')
        self.assertFalse(result.success)
        expected_result_string = """\
CaseClass: finished 4 tests
    FAILURE: 1
        CaseClass.test10: failed
"""
        self.assertEqual(str(result), expected_result_string)

    def test_blocked_tests(self):
        result = self.case_result
        result.add_failure('fail1', '-1')
        result.add_failure('fail2', '-2')
        result.add_failure('fail3', '-3')
        result.set_blocked_tests({
            'test6': {'fail2', 'fail3'},
            'test7': {'fail1', 'fail2', 'fail3'}
        })
        self.assertFalse(result.success)
        expected_result_string = """\
CaseClass: finished 4 tests
    FAILURE: 3
        CaseClass.fail1: -1
        CaseClass.fail2: -2
        CaseClass.fail3: -3
    BLOCKED: 2
        CaseClass.test6: ['CaseClass.fail2', 'CaseClass.fail3']
        CaseClass.test7: ['CaseClass.fail1', 'CaseClass.fail2', 'CaseClass.fail3']
"""
        self.assertEqual(str(result), expected_result_string)


class TestSuiteResult(unittest.TestCase):
    case_results = []

    @classmethod
    def setUpClass(cls):
        cls.case_results = []

        # successful test case
        case_result = pitest.TestCaseResult('CaseClass1')
        for i in range(4):
            case_result.add_success('test{}'.format(i))
        cls.case_results.append(case_result)

        # failed test case
        case_result = pitest.TestCaseResult('CaseClass2')
        for i in range(4):
            case_result.add_success('test{}'.format(i))
        case_result.add_failure('fail1', '-1')
        case_result.add_failure('fail2', '-2')
        cls.case_results.append(case_result)

        # failed test case with blocked tests
        case_result = pitest.TestCaseResult('CaseClass3')
        for i in range(4):
            case_result.add_success('test{}'.format(i))
        case_result.add_failure('fail1', '-1')
        case_result.add_failure('fail2', '-2')
        case_result.add_failure('fail3', '-3')
        case_result.set_blocked_tests({
            'test6': {'fail2', 'fail3'},
            'test7': {'fail1', 'fail2', 'fail3'}
        })
        cls.case_results.append(case_result)

    def test_success(self):
        result = pitest.TestSuiteResult('SuiteClass', None)
        result.add_test_case_result(self.case_results[0])
        self.assertTrue(result.success)
        expected_result_string = """\
(no args)
CaseClass1: finished 4 tests
================================================================

SUCCESS: 1

PASS
"""
        self.assertEqual(str(result), expected_result_string)

    def test_failure(self):
        result = pitest.TestSuiteResult('SuiteClass', None)
        result.add_test_case_result(self.case_results[0])
        result.add_test_case_result(self.case_results[1])
        self.assertFalse(result.success)
        expected_result_string = """\
(no args)
CaseClass1: finished 4 tests
CaseClass2: finished 4 tests
    FAILURE: 2
        CaseClass2.fail1: -1
        CaseClass2.fail2: -2
================================================================

SUCCESS: 1
FAILURE: 1

FAIL
"""
        self.assertEqual(str(result), expected_result_string)

    def test_blocked_tests(self):
        result = pitest.TestSuiteResult('SuiteClass', None)
        result.add_test_case_result(self.case_results[0])
        result.add_test_case_result(self.case_results[1])
        result.add_test_case_result(self.case_results[2])
        self.assertFalse(result.success)
        expected_result_string = """\
(no args)
CaseClass1: finished 4 tests
CaseClass2: finished 4 tests
    FAILURE: 2
        CaseClass2.fail1: -1
        CaseClass2.fail2: -2
CaseClass3: finished 4 tests
    FAILURE: 3
        CaseClass3.fail1: -1
        CaseClass3.fail2: -2
        CaseClass3.fail3: -3
    BLOCKED: 2
        CaseClass3.test6: ['CaseClass3.fail2', 'CaseClass3.fail3']
        CaseClass3.test7: ['CaseClass3.fail1', 'CaseClass3.fail2', 'CaseClass3.fail3']
================================================================

SUCCESS: 1
FAILURE: 2

FAIL
"""
        self.assertEqual(str(result), expected_result_string)

if __name__ == '__main__':
    unittest.main(verbosity = 0)
