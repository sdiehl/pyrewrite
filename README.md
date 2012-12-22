uaterm
------

Nanoaterm aims to be a micro term rewrite system written in
pure Python.

Usage
-----

```python
>>> from parse import parse
>>> parse('f(x,y)')
```

```python
>>> from matching import matches
>>> matches('f(x,y)', 'f(x,y)')
True

>>> matches('f(x,y)', 'f(x,z)')
False
```
