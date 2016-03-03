import case_base

# A -> B: A depends on B
# DemoCases0 - 5 are in deps.py. The complete dependency graph is:
#       8      10
#         \      \
#          \      \
#           \      \
#       0 ---> 1 ---> 3 ---> 4
#         \        /
#          \      /
#           \    /
#       9 ---> 2
class DemoCase8(case_base.CaseBase1):
    deps = [ 'DemoCase1' ]
class DemoCase9(case_base.CaseBase1):
    deps = [ 'DemoCase2' ]
class DemoCase10(case_base.CaseBase1):
    deps = [ 'DemoCase3' ]
