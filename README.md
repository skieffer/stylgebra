# Stylgebra: stylable algebraic expressions


Example
=======

Consider power expressions in SymPy:
```python
>>> from sympy import symbols
>>> x = symbols('x')
>>> expr1 = x**(-1)
>>> expr2 = x**(-2)
>>> expr1
1/x
>>> expr2
x**(-2)
```
By converting to a Stylgebra expression, we can set the rule for how to handle
negative exponents, like applying CSS styling to a web page:
```python
>>> from stylgebra.adapt import adapt_sympy_expr
>>> f = adapt_sympy_expr(expr2)
>>> f.format(rules={'Power': {'negative': 'sup'}})
'x^{-2}'
>>> f.format(rules={'Power': {'negative': 'frac'}})
'\\frac{1}{x^{2}}'
>>> f.format(rules={'Power': {'negative': 'inline'}})
'1/x^{2}'
```



The Problem
===========

This package supports the automatic generation of mathematical expressions, from
classes representing mathematical objects.

The problem is tricky because, while it is easy to represent any given mathematical
entity internally, we want quite fine-grained control over the way it is expressed
symbolically.

For example, if p = 7, here are several different ways of expressing the same sum:

    a_0 + a_1 + a_2 + ... + a_{p-2}
    a_0 + a_1 + ... + a_{p-2}
    a_0 + a_1 + a_2 + a_3 + a_4 + a_5
    a_{p-2} + a_{p-3} + ... + a_0
    a_{7-2} + a_{7-3} + ... + a_0
    a_5 + a_4 + ... + a_0

This problem is
essentially the same one that was solved in web browsers by HTML + CSS. The
HTML represents a hierarchical structure; the CSS lets us encode rules to
address elements of that structure and control the manner in which they are
displayed.

In the example above, the outermost structure might be "Sum". Its "styling"
includes choices like whether the terms within it should be ordered with
rising or falling subscripts, and whether an ellipsis should be used, and if
so how many terms should come before it.

Within the "Sum" structure are the individual "Term" structures. Within these
would be a "Base" and "Subscript". Within some of the Subscripts in our example
appears a "Variable" p. Among the "styling" modalities for a Variable would be
the choice to appear _by name_ ("p") or _by value_ ("7" in this case).

Solution
========

Our solution begins with a `Formal` class, and a whole suite of subclasses
representing the various kinds of structural elements suggested in our example,
like sums, subscripts, variables, etc. This is the "HTML" side of our solution,
i.e. the elements out of which to build the hierarchical structure that is a
mathematical object.

As for the "styling" or "CSS" side of our solution, each Formal class has a
`format` method, which accepts a _mode_ and an optional _rule set_. The mode
determines the manner of expression of this first element of the structure; it
is like everything that goes between one pair of braces {} in CSS. The rule set
allows us to define the modes for all the elements lying below the one on which
the `format` method was called; it is like a whole CSS file.

Where CSS rules are defined using "selectors" based on ids, classes, and other
properties, we instead ensure that each element of a formal structure has a
_path_ (a tree address), as well as an _id_, and our rules are based on
regular expression matching of ids and/or paths.

Documentation
=============

Sorry, at the moment proper docs are in the works.

A lot can be learned from the docstring of the `format()` method of
each of the `Formal___` classes in `expressions.py` and other modules.
