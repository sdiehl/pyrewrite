import parse
import matching
import rewrite
from terms import *
from matching import free, freev

import re
import os
from pprint import pprint
from collections import namedtuple, defaultdict, Counter

DEBUG = True

#------------------------------------------------------------------------
# Strategy Combinators
#------------------------------------------------------------------------

combinators = {
    'fail' : rewrite.fail,
    'id'   : rewrite.Id,
    '<+'   : rewrite.Choice,
    ';'    : rewrite.Seq,
}

#------------------------------------------------------------------------
# Errors
#------------------------------------------------------------------------

rparser = None
syntax_error = """

  File {filename}, line {lineno}
    {line}
    {pointer}

ATermSyntaxError: {msg}
"""

class RewriteSyntaxError(Exception):
    def __init__(self, lineno, col_offset, filename, text, msg=None):
        self.lineno     = lineno
        self.col_offset = col_offset
        self.filename   = filename
        self.text       = text
        self.msg        = msg or 'invalid syntax'

    def __str__(self):
        return syntax_error.format(
            filename = self.filename,
            lineno   = self.lineno,
            line     = self.text.split('\n')[self.lineno],
            pointer  = ' '*self.col_offset + '^',
            msg      = self.msg
        )

#------------------------------------------------------------------------
# Lexer

tokens = (
    'NAME', 'INT', 'DOUBLE', 'ARROW', 'STRING', 'COMB' #, 'CLAUSE'
)

literals = [
    ';',
    ',',
    '|',
    ':',
    '=',
    '(',
    ')',
    '{',
    '}',
    '[',
    ']',
]

t_NAME   = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_ignore = '\x20\x09\x0A\x0D'

# dynamically generate the regex for the Combinator token from
# the keys of the combinator dictionary
t_COMB  = '|'.join(map(re.escape, combinators.keys()))

unquote = re.compile('"(?:[^\']*)\'|"([^"]*)"')

def t_NEWLINE(t):
   r'\n'
   t.lexer.lineno += 1

def t_DOUBLE(t):
    r'\d+\.(\d+)?'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

def t_ARROW(t):
    r'->'
    return t

def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value.encode('ascii')
    t.value = unquote.findall(t.value)[0]
    return t

#def t_CLAUSE(t):
    #r'not|rec'
    #return t

def t_error(t):
    print("Unknown token '%s'" % t.value[0])
    t.lexer.skip(1)

#--------------------------------

RuleNode = namedtuple( 'Rule', ('label', 'lhs', 'rhs'))
StrategyNode = namedtuple('Strategy', ('label', 'combinator', 'args'))

start = 'definitions'

def p_definitions1(p):
    '''definitions : definitions rule
                   | definitions strategy'''
    p[0] = p[1] + [p[2]]

def p_definitions2(p):
    '''definitions : rule
                   | strategy'''
    p[0] = [p[1]]

#--------------------------------

def p_rule(p):
    '''rule : NAME ':' value ARROW value'''
    p[0] = RuleNode(p[1],p[3],p[5])

#--------------------------------

def p_strategy(p):
    '''strategy : NAME '=' strategy_value'''
    combs, args = p[3]
    p[0] = StrategyNode(p[1], combs, args)

def p_strategy_value1(p):
    '''strategy_value : strategy_value COMB strategy_value'''

    if isinstance(p[1], StrategyNode):
        p[0] = (p[2], [p[1]] + p[3])
    elif isinstance(p[3], StrategyNode):
        p[0] = (p[2], p[1] + [p[3]])
    else:
        p[0] = (p[2], [p[1],p[3]])

def p_strategy_value2(p):
    '''strategy_value : value'''
    p[0] = [p[1]]

#--------------------------------

def p_expr(p):
    '''expr : value'''
    p[0] = p[1]

#--------------------------------

def p_value(p):
    """value : term
             | appl
             | list
             | tuple
             | string
             | empty"""
    p[0] = p[1]

#--------------------------------

def p_term_double(p):
    "term : DOUBLE"
    p[0] = areal(p[1])

def p_term_int(p):
    "term : INT"
    p[0] = aint(p[1])

def p_term_term(p):
    "term : NAME"
    p[0] = aterm(p[1], None)

#--------------------------------

def p_appl(p):
    "appl : term '(' appl_value ')' "
    p[0] = aappl(p[1], p[3])

def p_appl_value1(p):
    "appl_value : expr"
    if p[1]:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_appl_value2(p):
    "appl_value : appl_value ',' appl_value"
    p[0] = p[1] + p[3]

#--------------------------------

def p_list(p):
    "list : '[' list_value ']' "
    p[0] = alist(p[2])

def p_list_value1(p):
    "list_value : expr"
    if p[1]:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_list_value2(p):
    "list_value : list_value ',' list_value"
    p[0] = p[1] + p[3]

#--------------------------------

def p_tuple(p):
    "tuple : '(' tuple_value ')' "
    p[0] = atupl(p[2])

def p_tuple_value1(p):
    "tuple_value : expr"
    if p[1]:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_tuple_value2(p):
    "tuple_value : tuple_value ',' tuple_value"
    p[0] = p[1] + p[3]

#--------------------------------

def p_string(p):
    "string : STRING"
    p[0] = astr(p[1])

#--------------------------------

def p_empty(t):
    "empty : "
    pass

#--------------------------------

def p_error(p):
    if p:
        raise RewriteSyntaxError(
            p.lineno,
            p.lexpos,
            '<stdin>',
            p.lexer.lexdata,
        )
    else:
        raise SyntaxError("Syntax error at EOF")

#--------------------------------

def _init():
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)

    lexer = lex.lex(lextab='rlex', optimize=0)
    parser = yacc.yacc(tabmodule='ryacc',outputdir=dir_path,debug=0,
        write_tables=1, optimize=0)
    return parser

def dslparse(pattern):
    parser = _init()
    return parser.parse(pattern)

#------------------------------------------------------------------------

class NoMatch(Exception):
    pass

class Strategy(object):

    def __init__(self, combinator, expr):
        self.left, self.right = expr
        self.combinator = combinator(self.left.rewrite, self.right.rewrite)

    def __call__(self, o):
        return self.combinator(o)

    rewrite = __call__

    def __repr__(self):
        return '%s(%s,%s)' % (
            self.combinator.__class__.__name__,
            (self.left),
            (self.right)
        )

#------------------------------------------------------------------------
# Rules
#------------------------------------------------------------------------

class Rule(object):
    def __init__(self, symtab, lpat, rpat, matcher, builder):
        self.matcher = matcher
        self.symtab = symtab
        self.builder = builder
        self.lpat = lpat
        self.rpat = rpat

    def rewrite(self, pattern):
        # This is transliteration of some OCaml code
        b = {} # bindings

        matches, captured = self.matcher(pattern)
        if matches:

            # Short circuit for trivial rewrites
            if len(self.rpat) == 0:
                return self.builder([])

            # Pattern match and ensure binding equality constraint
            for i,el in enumerate(captured):
                vi = self.lpat[i]
                if vi in b:
                    if b[vi] != el:
                        raise NoMatch()
                    else:
                        pass
                else:
                    b[self.lpat[i]] = el
            values = [b[j] for j in self.rpat]
            # TODO; prepend
            return self.builder(reversed(values))
        else:
            raise NoMatch()

    def __call__(self, pattern):
        return self.rewrite(pattern)

    def __repr__(self):
        return '%r -> %r' % (self.lpat, self.rpat)

class RuleBlock(object):
    def __init__(self, rules=None):
        self.rules = rules or []

    def add(self, rule):
        self.rules.append(rule)

    def rewrite(self, pattern):
        for rule in self.rules:
            try:
                return rule.rewrite(pattern)
            except NoMatch:
                continue
        raise NoMatch()

    def __call__(self, pattern):
        return self.rewrite(pattern)

    def __repr__(self):
        out = '[\n'
        for rule in self.rules:
            out += ' '*4 + repr(rule) + '\n'
        out += ']\n'
        return out

#------------------------------------------------------------------------
# AST -> Definnition Instances
#------------------------------------------------------------------------

def build_strategy(label, env, comb, args):
    env = env.copy() # mutable state is evil
    self = object() # forward declaration since rules can be self-recursive
    comb = combinators[comb]

    sargs = []

    for arg in args:
        # composition of combinators
        if isinstance(arg, tuple):
            subcomb, subargs = arg
            sargs.append(build_strategy(None, env, subcomb, subargs))

        if isinstance(arg, list):
            for iarg in arg:
                # look up the corresponding rewrite rule or
                # rewrite block and pass the rewrite hook to the
                # strategy combinator
                rr = env[iarg.term]
                sargs.append(rr)

    return Strategy(comb, sargs)


def build_rule(l, r):
    i,j = 0, 0

    lpat = []
    rpat = []

    symtab = {}

    for v in free(l):
        if v in symtab:
            lpat.append(symtab[v])
        else:
            symtab[v] = i
            lpat.append(i)
            i += 1

    for v in free(r):
        if v in symtab:
            rpat.append(symtab[v])
        else:
            raise Exception('Unbound variable')

    matcher = partial(matching.match, freev(l))
    builder = partial(matching.build, freev(r))

    rr = Rule(symtab, lpat, rpat, matcher, builder)
    return rr

#------------------------------------------------------------------------
# Module Constructions
#------------------------------------------------------------------------

def module(s, builtins=None):

    defs = dslparse(s)
    env= {}

    # A rewrite rule has the form L : l -> r, where L is the label of
    # the rule, and the term patterns l and r left hand matcher and
    # r the right hand builder. The right hand side symbol table is
    # augmented by the ``where`` clause.

    for df in defs:

        if isinstance(df, RuleNode):

            label, l, r = df
            rr = build_rule(l, r)

            if label in env:
                env[label].add(rr)
            else:
                env[label] = RuleBlock([rr])

        elif isinstance(df, StrategyNode):
            label, comb, args = df

            if label in env:
                raise Exception, "Strategy definition '%s' already defined" % label

            st = build_strategy(label, env, comb, args)
            env[label] = st
        else:
            raise NotImplementedError

    return env

res =  module('''
foo : A() -> B()
foo : B() -> A()
foo : Succ(0) -> 1
foo : Succ(1) -> 2
foo : Succ(x) -> Succ(Succ(x))
foo : Succ(x,y,z) -> Succ(Succ(x,y,y))

bar = foo ; foo
awk = foo ; foo ; foo
''')

#print res['foo'].rewrite(parse.parse('Succ(A())'))
#print res['foo'].rewrite(parse.parse('B()'))

#print res['bar'](parse.parse('B()'))
#print res['awk'](parse.parse('B()'))

#
# TODO: backtick support for shelling out to pure Python, or at
# ``literal_eval`` in locals()
#
# f(a,b) = `a + b`
#



#res = module('''

#Beta :
    #App(Lam(x, e1), e2) -> Let(x, e2, e1)

#Eta :
    #App(Lam(x, App(Lam(y, x), x), e2)) -> y

#EvalIf :
    #If(False(), e1, e2) -> e2

#EvalIf :
    #If(True(), e1, e2) -> e1

#PropIf :
    #If(B,F(X),F(Y)) -> F(If(B,X,Y))

#''')

#print res['Beta'](parse.parse('App(Lam(x, y), z)'))
#print res['EvalIf'](parse.parse('If(False(), x, y)'))
#print res['EvalIf'](parse.parse('If(True(), x, y)'))

#res = module('''
#bar: (1, 2, 2) -> (2, 1, 1)
#bar: (1, 2, 3) -> (1, 2, 3)

#fizz: [1, 2] -> [2, 1]
#fizz: 42 -> 24
#fizz: ([], "glorp", 8) -> ("glorp", 8, [])
#''')

#module('''foo = b''')

import sys
import argparse

banner = """Pyrewrite
------------------------------------
Type :help for for more information.
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('module', nargs='?', help='Module')
    args = parser.parse_args()

    # State
    mod = {}
    last = None
    stack = []

    if args.module:
        with open(args.module) as fd:
            mod = module(fd.read())

    print banner
    import readline
    import pprint
    readline.parse_and_bind('')


    while True:
        try:
            line = raw_input('>> ').strip()
        except EOFError:
            break

        if line.startswith('?'):
            at = parse.parse(line[1:])
            matcher = partial(matching.match, freev(at))
            matched, localbind = matcher(last)
            stack.extend(localbind)

            if matched:
                print stack
            else:
                print 'failed'
        elif line.startswith('!'):
            try:
                rr = mod[line[1:].strip()]
                last = rr.rewrite(last)
                print last
            except NoMatch:
                print 'failed'
        elif line.startswith('s'):
            try:
                rr = mod[line[1:].strip()]
                print rr
            except KeyError:
                print "No such rule or strategy", line[1:]

        elif line.startswith(':t'):
            try:
                at = parse.parse(line[2:])
                print type(at).__name__
            except Exception as e:
                print e
        elif line.startswith(':bindings'):
            if stack:
                print stack
            continue
        elif line.startswith(':let'):
            defn = parse.parse(line[4:])
            p = dslparse(defn)
            print p
        elif line.startswith(':browse'):
            pprint.pprint(mod)
        elif line.startswith(':help'):
            pass
        else:
            stack = []
            try:
                last = parse.parse(line)
                print last
            except EOFError:
                pass
            except Exception as e:
                print e

if __name__ == '__main__':
    main()
