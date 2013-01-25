from rewrite import aparse
from rewrite.dsl import dslparse, module

#------------------------------------------------------------------------

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
    dslparse(simple)

def test_simple_module():
    module(simple)

#------------------------------------------------------------------------

patterns = """
EvalIf :
    If(False(), e1, e2) -> e2

EvalIf :
    If(True(), e1, e2) -> e1

PropIf :
    If(B,@F(X),@F(Y)) -> F(If(B,X,Y))
"""

def test_patterns_parse():
    dslparse(patterns)

def test_patterns_module():
    module(patterns)

#------------------------------------------------------------------------

simple_state = """
foo : A(x,y) -> A(y,x)
bar : A(x,y) -> A(y,x)
"""

simple_expected = """
{'foo': [
    [0, 1] -> [1, 0]
]
}
"""

def test_state_machine():
    repr(module(simple_state)) == simple_expected

#------------------------------------------------------------------------

simple_rr = """
foo : A() -> B()
foo : B() -> C()

bar = foo ; foo
"""

def test_rewrite_simple():
    a = aparse('A()')
    b = aparse('B()')
    c = aparse('C()')

    mod = module(simple_rr)

    rule = mod['foo']

    assert rule(a) == b
    assert rule(b) == c
    assert rule(rule(a)) == c

def test_rewrite_simple2():
    a = aparse('A()')
    b = aparse('B()')
    c = aparse('C()')

    mod = module(simple_rr)

    rule = mod['bar']

    assert rule(a) == c
