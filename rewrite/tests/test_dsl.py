from rewrite.dsl import dslparse, module

simple = """
foo : A() -> B()
foo : B() -> A()

bar : Succ(0) -> 1
bar : Succ(1) -> 2
bar : Succ(x) -> Succ(Succ(x))

both : f(x,x) -> 1
both : f(x,y) -> 0

a0 = foo ; foo
a1 = foo ; foo ; foo
a2 = foo <+ foo ; foo
"""

def test_simple_parse():
    a = dslparse(simple)

def test_simple_module():
    a = module(simple)
    print a
