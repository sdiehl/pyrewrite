import re
from functools import partial
from collections import namedtuple, OrderedDict

import ply.lex as lex
import ply.yacc as yacc

class ATermBase(object):
    """ Base for aterms """

    # Specifies child attributes
    _fields = []

    def __init__(self, annotation=None):
        self.annotation = annotation

class ATerm(ATermBase):

    def __init__(self, label, **kwargs):
        super(ATerm, self).__init__(**kwargs)
        self.label = label

    def __str__(self):
        return str(self.label) + self.metastr

    def _matches(self, query):
        return self.label == query

    def __repr__(self):
        return str(self)

class AAppl(ATermBase):

    _fields = ['spine', 'args']

    def __init__(self, spine, args, **kwargs):
        super(AAppl, self).__init__(**kwargs)
        assert isinstance(spine, ATerm)
        self.spine = spine
        self.args = args

    def _matches(self, query):
        if query == '*':
            return True

        spine, args, _ = sep.split(query)
        args = args.split(',')

        if len(self.args) != len(args):
            return False

        # success
        if spine.islower() or self.spine.label == spine:
            _vars = {}
            argm = [b.islower() or a._matches(b) for a,b in zip(self.args, args)]

            if spine.islower():
                _vars[spine] = self.spine

            for i, arg in enumerate(args):
                if argm[i]:
                    _vars[arg] = self.args[i]

            return _vars

        else:
            return False

    def __str__(self):
        return str(self.spine) + arepr(self.args, '(', ')') + self.metastr

    def __repr__(self):
        return str(self)

class AAnnotation(ATermBase):

    def __init__(self, ty=None, annotations=None):
        self.ty = ty or None

        if annotations is not None:
            # Convert annotations to aterms
            annotations = list(annotations)
            for i, annotation in enumerate(annotations):
                if not isinstance(annotation, ATermBase):
                    annotations[i] = ATerm(annotation)

        self.meta = annotations or []

    @property
    def annotations(self):
        terms = map(ATerm, (self.ty,) + tuple(self.meta))
        return arepr(terms, '{', '}')

    def __contains__(self, key):
        if key == 'type':
            return True
        else:
            return key in self.meta

    def __getitem__(self, key):
        if key == 'type':
            return self.ty
        else:
            return key in self.meta

    def _matches(self, value, meta):
        if value == '*':
            vmatch = True
        else:
            vmatch = self.bt._matches(value)

        if meta == ['*']:
            mmatch = True
        else:
            mmatch = all(a in self for a in meta)

        if vmatch and mmatch:
            return vmatch
        else:
            return False

    def __str__(self):
        return self.annotations

    def __repr__(self):
        return str(self)

class AString(ATermBase):
    def __init__(self, s, **kwargs):
        super(AString, self).__init__(**kwargs)

        # must be ascii
        assert isinstance(s, str)
        self.s = s

    def __str__(self):
        return '"%s"' % (self.s + self.metastr)

    def __repr__(self):
        return str(self)

class AInt(ATermBase):
    def __init__(self, n, **kwargs):
        super(AInt, self).__init__(**kwargs)
        self.n = n

    def _matches(self, value):
        if value.islower():
            return True
        else:
            return self.n == int(value)

    def __str__(self):
        return str(self.n) + self.metastr

    def __repr__(self):
        return str(self)

class AFloat(ATermBase):
    def __init__(self, n, **kwargs):
        super(AFloat, self).__init__(**kwargs)
        self.n = n

    def __str__(self):
        return str(self.n) + self.metastr

    def __repr__(self):
        return str(self)

class AList(ATermBase):
    def __init__(self, *elts, **kwargs):
        super(AList, self).__init__(**kwargs)
        self.elts = elts

    def __str__(self):
        return arepr(self.elts, '[', ']') + self.metastr

    def __repr__(self):
        return str(self)

#------------------------------------------------------------------------
# Named Tuple Implementation
#------------------------------------------------------------------------

aterm = namedtuple('aterm', ('term', 'annotation'))
astr  = namedtuple('astr', ('val',))
aint  = namedtuple('aint', ('val',))
areal = namedtuple('areal', ('val',))
aappl = namedtuple('aappl', ('spine', 'args'))
atupl = namedtuple('atupl', ('args'))
aplaceholder = namedtuple('aplaceholder', ('type','args'))
