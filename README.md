pyrewrite
---------

Pyrewrite aims to be a micro term rewrite library written in pure Python.

Pyrewrite has no dependencies other than the Python standard library.

Usage
-----

```python
>>> from rewrite import parse
>>> parse('f(x,y)')
f(x,y)
```

```python
>>> from rewrite import matches
>>> matches('f(x,y)', 'f(x,y)')
True

>>> matches('f(x,y)', 'f(x,z)')
False
```

```python
>>> from rewrite import match
>>> match('f(<term>)', 'f(x)')
(True, [x])

>>> match('f(<term>,<int>)', 'f(x,1)')
(True, [x, 1])

match('succ(<appl(<term>)>)', 'succ(succ(zero))')
(True, [succ, zero])
```

Theory
------

Term rewriting is the procedure for manipulating abstract system
of symbols where the objects are terms, or expressions with nested
sub-expressions.

The term structure in such a system is usually presented using a
grammar. In contrast to string rewriting systems, whose objects are flat
sequences of symbols, the objects of a term rewriting system form a term
algebra, which can be visualized as a tree of symbols, the structure of
the tree fixed by the signature used to define the terms.

```
t : bt                 -- basic term
  | bt {ty,m1,...}     -- annotated term

bt : C                 -- constant
   | C(t1,...,tn)      -- n-ary constructor
   | (t1,...,tn)       -- n-ary tuple
   | [t1,...,tn]       -- list
   | "ccc"             -- quoted string ( explicit double quotes )
   | int               -- integer
   | real              -- floating point number
```

A rewrite rule has the form ``L : l -> r``, where L is the label of the
rule, and the term patterns ``l`` and ``r`` left hand matcher and ``r``
the right hand builder.

**Match** and **Build**

The specification of a rewrite rule system consists of two actions
*matching* and *building*. Matching deconstructs terms into into a
environment object with term objects bound to identifiers in the
context based on deconstruction pattern.

Building is the dual notation to matching, it constructs term
terms from environments of bindings based a construction pattern.

**Blocks**

```
Eval : Not(True)      -> False
Eval : Not(False)     -> True
Eval : And(True, x)   -> x
Eval : And(x, True)   -> x
Eval : And(False, x)  -> False
Eval : And(x, False)  -> False
Eval : Or(True, x)    -> True
Eval : Or(x, True)    -> True
Eval : Or(False, x)   -> x
Eval : Or(x, False)   -> x
Eval : Impl(True, x)  -> x
Eval : Impl(x, True)  -> True
Eval : Impl(False, x) -> True
Eval : Eq(False, x)   -> Not(x)
Eval : Eq(x, False)   -> Not(x)
Eval : Eq(True, x)    -> x
Eval : Eq(x, True)    -> x

eval = bottomup(repeat(Eval))
```

**Strategies**

```
all(s)     Apply parameter strategy s to each direct subterm
rec(s)

s1;s2      Sequential composition
s1<+s2     Deterministic choice first try s1, s2 if fail
s1<s2+s3   if s1 succeeds then commit s2, else s3
```

```
try(s)       = s <+ id
repeat(s)    = try(s; repeat(s))
topdown(s)   = s; all(topdown(s))
bottomup(s)  = all(bottomup(s)); s
alltd(s)     = s <+ all(alltd(s))
downup(s)    = s; all(downup(s)); s
innermost(s) = bottomup(try(s; innermost(s)))
```

**Confluence**

**As-Patterns**

Examples
-------

**Peano**

**SKI**

**Lambda**

The simple lambda calculus consists of a set of expressions
called *Expr*:

```haskell
Expr = Var | App | Lam
```

With the following constructions:

```haskell
Var (x : Sym)
App (e0 : Expr) (e1 : Expr)
Lam (x : Sym) (e0 : Expr)
```

**Python**

Credits
-------

Inspired by the [StrategoXT](http://strategoxt.org/) project.

Also inspired by the [Basil project](https://code.google.com/p/basil/)
by Jon Riehl
