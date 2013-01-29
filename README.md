pyrewrite
---------

Pyrewrite aims to be a micro term rewrite library written in pure Python.

Pyrewrite has no dependencies other than the Python standard library.

The broad goal of this project is to build a declarative rewrite engine
in which domain experts and algorithm programmers can collaborate to
develop transformation passses on Blaze expressions at a higher level,
with the end goal being to inform more performant computations and
scheduling.

Also because Python doesn't have a good term rewriting engine and this
is an essential part to building a vibrant compiler infastructure around
CPython.

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

The application of rules can be a *Normalization* if it is the
exhaustive application of rules. The ``eval`` rule above is normalizing.

A *normal form* for an expression is a expression where no
subterm can be rewritten.

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

A term rewrite system need not terminate, for example the following is
a *non-terminating* rewrite system that results in an infinite rewrite
loop:

```
foo : A() -> B() 
foo : B() -> A()

rule : repeat(foo)
```

A term rewrite system is said to *confluent* when given multiple
possibilities of rule application, all permutations of application
lead to the same result regardless of order. The general problem
of determining whether a term-rewrite system is confluent is very
difficult.

**Nonlinear Patterns**

This pattern of this form will match only if all occurrences of the same
variable in the left-hand side pattern bind to the same value.

```
foo: f(x,x) -> x
```

The above matches ``f(1,1)`` but not ``f(1,2)``.

This behavior differs from Haskell and is is to my knowledge only found
in the Pure programming language.

**As-Patterns**

**Recursion**

Examples
-------

**Lambda**

The simple lambda calculus consists of a set of expressions
*Sym* and *Expr* with the following constructions:

```haskell
Sym = String
Expr = Var Sym | App Expr Expr | Lam Sym Expr
```

**Peano**

**SKI**

```
S = lambda x: lambda y: lambda z: x(z)(y(z))
K = lambda x: lambda y: x
I = lambda x: x
```

**ASDL**

TODO

**SymPy**

TODO

**Blaze**

TODO

Credits
-------

- [StrategoXT](http://strategoxt.org/) project.

- [Basil project](https://code.google.com/p/basil/) by Jon Riehl

- [PLT Scheme](http://download.plt-scheme.org/doc/360/html/mzlib/mzlib-Z-H-25.html#node_chap_25)

- Pure and the paper and "Left-to-right tree pattern matching" by Albert Gräf
