from rewrite.parse import parse
from rewrite.matching import match, make
from rewrite.terms import *

def test_parser_sanity():

    a0 = parse('f')
    a1 = parse('f(x)')
    a2 = parse('f(x,y)')
    a3 = parse('(x,y)')
    a4 = parse('f(x,f(x,y))')
    a5 = parse('f(1,2,3)')
    a6 = parse('f([1,2,3])')
    a7 = parse('(1,2,3)')

    assert repr(a0) == 'f'
    assert repr(a1) == 'f(x)'
    assert repr(a2) == 'f(x, y)'
    assert repr(a3) == '(x, y)'
    assert repr(a4) == 'f(x, f(x, y))'
    assert repr(a5) == 'f(1, 2, 3)'
    assert repr(a6) == 'f([1, 2, 3])'
    assert repr(a7) == '(1, 2, 3)'

    parse('f(x,y){abc, foo}')
    parse('f(x,y){abc, foo, awk}')
    parse('f(x,y{fizzbang})')
    parse('f{x}')
    parse('f{[(a,b),(c,d)]}')

    parse('[1,2, 3]')
    parse('["foo"]')
    parse('[1, 2, 3.14]')
    parse('[a,b,c,f(b),f(b,1),1.2,1.3]')
    parse('[c,f(b,1),a,b,f(b),1.3,1.2]')
    parse('[[1,2],[1]]')
    parse('[]{[a,a]}')
    parse('f(<int>,<real>,<placeholder>,<str>)')
    parse('f(<list>,[])')
    parse('<appl(1,2)>')
    parse('<term>{[a,b]}')

    parse('Pow(<term>,<term>)')
    parse('Mul(Array(),Array())')
    parse('Mul(Array,Array)')
    parse('Add(2,3{dshape("foo, bar, 2")})')
    parse('Add(2{dshape("int"),62764584},3.0{dshape("double"),62764408})')

def test_matching():
    match('x', 'x')
    match('x', 'y')
    match('x{foo}', 'x{foo}')

    match('f(x,y)', 'f(x,y)')
    match('f(x,g(x,y))', 'f(x,g(x,y))')
    match('f(<int>,g(x,y))', 'f(1,g(x,y))')
    match('f(<int>,g(x,y))', 'f(1,g(x,y))')
    match('f(1,<appl(x,y)>)', 'f(1,g(x,y))')
    match('f(1,<appl(x,<term>)>)', 'f(1,g(x,3))')

def test_make():
    make('f(<int>)', aint(1))
    make('f(x, y, g(<int>,<int>))', aint(1), aint(2))
    make('<appl(x,y)>', aterm('x', None))
