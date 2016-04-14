import case_base

class DemoClass3(case_base.CaseBase3):
    _internal_deps = { 'test_foo': 'test_bar' }
    def run(self):
        pass
    def test_foo(self):
        pass
    def test_bar(self):
        pass
