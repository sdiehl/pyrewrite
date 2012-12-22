#------------------------------------------------------------------------
# Rewrite Combinators
#------------------------------------------------------------------------

Id = lambda s: s

def Fail():
    raise STFail()

class STFail(Exception):
    pass

compose = lambda f, g: lambda x: f(g(x))

class Fail(object):

    def __init__(self):
        pass

    def __call__(self, o):
        raise STFail()

class Choice(object):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right
        assert left and right, 'Must provide two arguments to Choice'

    def __call__(self, s):
        try:
            return self.left(s)
        except STFail:
            return self.right(s)

class Ternary(object):
    def __init__(self, s1, s2, s3):
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3

    def __call__(self, o):
        try:
            val = self.s1(o)
        except STFail:
            return self.s2(val)
        else:
            return self.s3(val)

class Fwd(object):

    def __init__(self):
        self.p = None

    def define(self, p):
        self.p = p

    def __call__(self, s):
        if self.p:
            return self.p(s)
        else:
            raise NotImplementedError('Forward declaration, not declared')

class Repeat(object):
    def __init__(self, p):
        self.p = p

    def __call__(self, s):
        val = s
        while True:
            try:
                val = self.p(val)
            except STFail:
                break
        return val

class All(object):
    def __init__(self, s):
        self.s = s

    def __call__(self, o):
        if isinstance(o, AAppl):
            return AAppl(o.spine, map(self.s, o.args))
        else:
            return o

class Some(object):
    def __init__(self, s):
        self.s = s

    def __call__(self, o):
        if isinstance(o, AAppl):
            largs = []
            for a in o.args:
                try:
                    largs.append(self.s(a))
                except STFail:
                    largs.append(a)
            return AAppl(o.spine, largs)
        else:
            raise STFail()

class Seq(object):
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2

    def __call__(self, o):
        return self.s2(self.s1(o))

class Try(object):
    def __init__(self, s):
        self.s = s

    def __call__(self, o):
        try:
            return self.s(o)
        except STFail:
            return o

class Topdown(object):
    def __init__(self, s):
        self.s = s

    def __call__(self, o):
        val = self.s(o)
        return All(self)(val)

class Bottomup(object):
    def __init__(self, s):
        self.s = s

    def __call__(self, o):
        val = All(self)(o)
        return self.s(val)

class Innermost(object):
    def __init__(self, s):
        self.s = s

    def __call__(self, o):
        return Bottomup(Try(Seq(self.s, self)))(o)

class SeqL(object):
    def __init__(self, *sx):
        self.lx = reduce(compose,sx)

    def __call__(self, o):
        return self.lx(o)

class ChoiceL(object):
    def __init__(self, *sx):
        self.sx = reduce(compose,sx)

    def __call__(self, o):
        return self.sx(o)
