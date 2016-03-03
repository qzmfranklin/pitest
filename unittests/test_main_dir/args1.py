import pitest

__pitest_main_default_args_name__ = 'my_args'

my_args = pitest.TestCaseArgs()
my_args.set_method_args('__init__',
        args = ('Anndee', ),
        kwargs = { 'kwarg0': 'KoolArg' })
my_args.set_method_args('test',
        args = ('naathing', ),
        kwargs = { 'kwarg1': 'at owl' })

my_args2 = pitest.TestCaseArgs()
my_args2.set_method_args('__init__',
        args = ('Bashii', ),
        kwargs = { 'kwarg0': 'KoolArg2' })
my_args2.set_method_args('test',
        args = ('naathing', ),
        kwargs = { 'kwarg1': 'at owlll' })
