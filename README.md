pyrewrite
---------

Pyrewrite aims to be a micro term rewrite library written in pure Python.

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
