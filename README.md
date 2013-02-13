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
E : Impl(x, y) -> Or(Not(x), y)
E : Eq(x, y) -> And(Impl(x, y), Impl(y, x))

E : Not(Not(x)) -> x

E : Not(And(x, y)) -> Or(Not(x), Not(y))
E : Not(Or(x, y)) -> And(Not(x), Not(y))

E : And(Or(x, y), z) -> Or(And(x, z), And(y, z))
E : And(z, Or(x, y)) -> Or(And(z, x), And(z, y))

dnf = repeat(topdown(E) <+ id)
```

Compiles into a rewrite environement with the following
signature:

```
{'E': [
    Impl(<term>, <term>) => Or(Not(<term>), <term>) ::
	 ['x', 'y'] -> ['x', 'y']
    Eq(<term>, <term>) => And(Impl(<term>, <term>), Impl(<term>, <term>)) ::
	 ['x', 'y'] -> ['x', 'y', 'y', 'x']
    Not(Not(<term>)) => <term> ::
	 ['x'] -> ['x']
    Not(And(<term>, <term>)) => Or(Not(<term>), Not(<term>)) ::
	 ['x', 'y'] -> ['x', 'y']
    Not(Or(<term>, <term>)) => And(Not(<term>), Not(<term>)) ::
	 ['x', 'y'] -> ['x', 'y']
    And(Or(<term>, <term>), <term>) => Or(And(<term>, <term>), And(<term>, <term>)) ::
	 ['x', 'y', 'z'] -> ['x', 'z', 'y', 'z']
    And(<term>, Or(<term>, <term>)) => Or(And(<term>, <term>), And(<term>, <term>)) ::
	 ['z', 'x', 'y'] -> ['z', 'x', 'z', 'y']
]
,
 'dnf': Repeat(Choice(Topdown(E),function))}
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

**ASDL**

The Zephyr Abstract Syntax Description Lanuguage (ASDL) is a description
language designed to describe the tree-like data structures in
compilers. Specically it underpins the parser of Python itself (
see ``Parser/Python.asdl`` ).

```cpp
module Python
{

	stmt = FunctionDef(identifier name, arguments args,
	      | For(expr target, expr iter, stmt* body, stmt* orelse)
	      | While(expr test, stmt* body, stmt* orelse)
	      | If(expr test, stmt* body, stmt* orelse)
	      | With(expr context_expr, expr? optional_vars, stmt* body)

}
```

**Blaze**

TODO

Credits
-------

- [StrategoXT](http://strategoxt.org/) project.

- [Basil project](https://code.google.com/p/basil/) by Jon Riehl

- [PLT Scheme](http://download.plt-scheme.org/doc/360/html/mzlib/mzlib-Z-H-25.html#node_chap_25)

- Pure and the paper and "Left-to-right tree pattern matching" by Albert Gräf

License
-------

Copyright (c) 2012, Continuum Analytics, Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
