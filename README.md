pyrewrite
---------

Pyrewrite aims to be a micro term rewrite library written in pure Python.

Usage
-----

```python
>>> from rewrite import parse
>>> parse('f(x,y)')
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
>>> matches('f(<term>)', 'f(x)')
x

>>> matches('f(<term>,<int>)', 'f(x,1)')
[aterm('x'), aint('1')]
```
