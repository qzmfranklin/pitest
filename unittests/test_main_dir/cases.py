import pitest

class CaseBase(pitest.TestCaseBase):
    def __init__(self, arg0, *, kwarg0):
        print('{}.__init__({}, kwarg0 = {})'
              .format(self.__class__.__name__, arg0, kwarg0))
    def test_foo(self, arg1, *, kwarg1):
        print('{}.test_foo({}, kwarg1 = {})'
              .format(self.__class__.__name__, arg1, kwarg1))

class Case1(CaseBase):
    pass
class Case2(CaseBase):
    pass
class Case3(CaseBase):
    pass
class Case4(CaseBase):
    def test_bar(self, arg1, *, kwarg1):
        print('{}.test_bar({}, kwarg1 = {})  <===  Only Case4 has test_bar()'
              .format(self.__class__.__name__, arg1, kwarg1))
class Case5(CaseBase):
    pass
