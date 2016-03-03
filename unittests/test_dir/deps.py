import case_base

# A -> B: A depends on B
# {0} -> {1, 2} -> {3} -> {4}
class DemoCase0(case_base.CaseBase1):
    deps = [ 'DemoCase1', 'DemoCase2' ]
class DemoCase1(case_base.CaseBase1):
    deps = [ 'DemoCase3' ]
class DemoCase2(case_base.CaseBase1):
    deps = [ 'DemoCase3' ]
class DemoCase3(case_base.CaseBase1):
    deps = [ 'DemoCase4' ]
class DemoCase4(case_base.CaseBase1):
    pass
