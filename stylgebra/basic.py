# --------------------------------------------------------------------------- #
#   Stylgebra                                                                 #
#                                                                             #
#   Copyright (c) 2020-2023 Steve Kieffer                                     #
#                                                                             #
#   Licensed under the Apache License, Version 2.0 (the "License");           #
#   you may not use this file except in compliance with the License.          #
#   You may obtain a copy of the License at                                   #
#                                                                             #
#       http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                             #
#   Unless required by applicable law or agreed to in writing, software       #
#   distributed under the License is distributed on an "AS IS" BASIS,         #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
# --------------------------------------------------------------------------- #

import re
import inspect

from sympy import Integer as SympyInteger
from sympy import Rational as SympyRational

from stylgebra.excep import FormalExcep


class MM(str):
    """
    Use this subclass of str to represent strings intended to go inside LaTeX
    math modes. It provides smart concatenation so that, if a:T means a is a string
    of type T, then we have:

            a:mm + b:mm   = ab:mm
            a:mm + b:str  = $a$b:str
            a:str + b:mm  = a$b$:str

    and of course

            a:str + b:str = ab:str

    is still true!
    """

    def __new__(cls, value):
        """
        We want `MM(a)` to work for many different types of argument `a`.
        If `a` is a str, then we represent that string in math mode.
        If `a` is another MM, we want to represent the same string it does.
        If `a` is anything else, we want to convert it into a pure string,
        and then represent that string in math mode.
        """
        # While the given value is not in the subclass hierarchy of `str`, or
        # it is but lies at or below `MM`, then convert it into a `str`.
        while isinstance(value, MM) or not isinstance(value, str):
            value = str(value)
        # Now we can make a plain string on that value.
        self = str.__new__(cls, value)
        # And store it as the plain string that we represent.
        self.plain_str = value
        return self

    def __str__(self):
        """
        Use this to recover the pure string. In other words,
        if a:mm then str(a):str.
        """
        return self.plain_str

    def __add__(self, other):
        # If other string is empty, don't let that take us out of math mode,
        # but do return a brand new MM.
        if len(other) == 0: return MM(self)
        # Sum of MM's is another MM.
        if isinstance(other, MM):
            return MM(self.plain_str + other.plain_str)
        # If added to plain string, surround with $'s and downgrade to plain.
        else:
            return f'${self}${other}'

    def __radd__(self, other):
        if len(other) == 0: return MM(self)
        if isinstance(other, MM):
            return MM(other.plain_str+self.plain_str)
        else:
            return f'{other}${self}$'

    def join(self, iterable):
        """
        If a:mm and L = [b0:mm, ..., bk:mm] then a.join(L):mm.
        """
        s = ''
        first = True
        for t in iterable:
            if first:
                s = t
                first = False
            else:
                s += self + t
        return s


def bracket_expression(style, expression):
    """
    Put brackets of a given style around a given expression.

    :param style: a bracket style; if invalid, expression will be returned
        unchanged.
    :param expression: the expression (str) to be bracketed

    :return: the modified expression
    """
    B = {
        'round': ("(", ")"),
        'square': (r'\[', r'\]'),
        'curly': (r'\lbrace', r'\rbrace'),
    }.get(style)
    if B is not None:
        expression = MM(r'\left') + MM(B[0]) + expression + MM(r'\right') + MM(B[1])
    return expression


def mbox(s):
    return s if isinstance(s, MM) else MM(r'\mbox{' + s + '}')


def wrap(obj):
    """
    Wrap an object, as needed, to make it a Formal object.
    """
    from stylgebra.expressions import FormalInteger, FormalQuotient, FormalEllipsis, FormalString
    if isinstance(obj, int):
        obj = FormalInteger(obj)
    elif isinstance(obj, SympyInteger):
        obj = FormalInteger(int(obj))
    elif isinstance(obj, SympyRational):
        n = int(obj.numerator)
        d = int(obj.denominator)
        obj = FormalQuotient(n, d)
    elif obj == Ellipsis:
        obj = FormalEllipsis()
    elif isinstance(obj, str):
        obj = FormalString(obj)
    return obj


class FormOpt:
    """
    Options for the 'form' property which is a part of the mode definition
    for almost all Formal classes.
    """
    NAME = 'name'
    VALUE = 'value'
    SYMBOLIC = 'symbolic'
    VERBAL = 'verbal'
    # Convenience for classes where 'value' and 'symbolic' are synonymous:
    valsym = [VALUE, SYMBOLIC]


EXPR_PATH_DELIMITER = '-'

# Check that a selector chain is at least a space-separated list
# of nonempty strings, starting with at least one nonempty string.
BASIC_SEL_CHAIN_PATTERN = re.compile(r'^\S+(\s+\S+)*$')


class ExpressionPath:
    """
    In an expression tree, Formal objects are the nodes, while "roles" are the edges.

    By a "role" we mean a string defining the role a subnode is playing
    relative to its parent node. For example, within a FormalPower there are
    two roles: "base" and "power". Within a FormalSum there is one role for
    each term, with the form `"term%d" % i`.

    This class represents a path of alternating nodes and edges leading down from
    the root of an expression tree to a single node within it.

    Because such a path alternates (node, role, node, role, ...), and because it
    always begins with a node and ends with a role, it always contains an equal
    number of nodes and roles.
    """

    def __init__(self, ancestors=None, roles=None, parent=None, role=None):
        self.ancestors = ancestors or []
        self.roles = roles or []
        if parent is not None and role is not None:
            self.append(parent, role)

    def append(self, parent, role):
        self.ancestors.append(parent)
        self.roles.append(role)

    def rolepath(self):
        return EXPR_PATH_DELIMITER.join(self.roles)

    def pop(self):
        a = self.ancestors.pop()
        r = self.roles.pop()
        return a, r

    def __str__(self):
        s = ''
        for a, r in zip(self.ancestors, self.roles):
            s += f'({a})-{r}-'
        return s

    def __bool__(self):
        return len(self) > 0

    def __len__(self):
        return len(self.roles)

    def __getitem__(self, key):
        # See <https://stackoverflow.com/a/16033058>
        if isinstance(key, slice):
            A = self.ancestors[key]
            R = self.roles[key]
            return ExpressionPath(ancestors=A, roles=R)
        return self.ancestors[key], self.roles[key]

    def __add__(self, other):
        return ExpressionPath(
            ancestors=self.ancestors + other.ancestors,
            roles=self.roles + other.roles
        )


class PathMatch:

    def __init__(self, end_pattern, exp_path):
        """
        :param end_pattern: string giving a desired final portion of a node path, with
            path segments separated by hyphens `-`.
            May use bracket notation `[i]` to indicate numeric matching groups.
        :param exp_path: the ExpressionPath leading up to the present point.

        For example, suppose

            end_pattern = 'cat-foo[i]bar[j]'
            rolepath = 'baz3-cat-foo17bar81'

        then...

        """
        p = '(?:^|-)%s$' % re.sub(r'\[([a-zA-Z]\w*)\]', r'(?P<\1>\\d+)', end_pattern)
        rolepath = exp_path.rolepath()
        m = re.search(p, rolepath)
        if m is None:
            self.matched = False
        else:
            self.matched = True
            self.indices = {k:int(v) for k, v in m.groupdict().items()}
            n = len(end_pattern.split('-'))
            self.num_segments_matched = n
            self.rolepath_prefix = rolepath[:m.span()[0]]
            self.exp_path_prefix = exp_path[:] if n == 1 else exp_path[:-n+1]


class Formal:

    def __init__(self, value=None, name=None, id=None, mode=None):
        r"""
        :param value: if provided, this should be an object that represents or defines
            the actual (numerical or other) value of the object in question. Not all
            objects will have a value.

        :param name: this should be a string giving the LaTeX you would use (without
            dollar signs) for the name by which you are calling this object within
            a given discussion.

        :param id: optional string with which to identify this object in formatting
            rules. If not provided, will be set equal to name.

        :param mode: this will be the initial default mode for governing the
            execution of the `format` method. It can be updated at any time using
            the `mode` method. If `None` is passed, we change this to an empty
            dictionary.
        """
        self._value = value
        self._name = name
        self._id = id or name
        self._mode = mode if mode is not None else {}

    def format(self, mode=None, rules=None, path=None, modifier=None):
        return ''

    def value(self, *args):
        if args:
            self._value = args[0]
        else:
            return self._value

    def name(self, *args):
        if args:
            self._name = args[0]
        else:
            return self._name

    def id(self, *args):
        if args:
            self._id = args[0]
        else:
            return self._id

    def mode(self, *args):
        if args:
            self._mode = args[0]
        else:
            return self._mode

    def decideMode(self, mode=None, rules=None, path=None, modifier=None):
        """
        Figure out which mode this object should be using during its `format` method.

        If a `mode` is given directly, take that.
        If not, try to find a mode in the rules.
        If that fails too, use this object's current default mode.
        However, in all these cases, if a modifier was given, apply it
            before returning. If the mode and modifier are both dictionaries,
            the mode will be upated by the modifier; otherwise the modifier
            should be a callable, and we apply it to the mode.
        """
        # If the mode is not given explicitly, we try to infer it from the rules.
        if mode is None and rules is not None:
            mode = self.searchRules(rules, path)
        # If we still don't have a mode, use our current default.
        if mode is None:
            mode = self.mode()
        # Modify?
        if modifier is not None:
            if isinstance(modifier, dict) and isinstance(mode, dict):
                mode = {**mode, **modifier}
            elif callable(modifier):
                mode = modifier(mode)
        return mode

    def searchRules(self, rules, path):
        """
        Search a (ordered) dictionary of rules for one that matches this object
        at the given expression path.

        Return the mode for the first rule that matches, or None.

        If a mode matches and is callable, we return the result of calling it
        at the indices matched by the rule.

        :param rules: should be a dictionary-like object. Keys are strings giving selectors,
            and values are the format modes that should be used if the rules match.

            The rules will be processed in order, and the first match will be accepted.
            So from Python 3.6 and onward, you can just use an ordinary dictionary, since these
            are now ordered. Before that, you should use collections.OrderedDict.
            See <https://stackoverflow.com/a/39980744>

        :param path: the path of the object; must be a string

        :return: the mode of the first rule that matched, or None
        """
        if path is None: path = ExpressionPath()
        for sel_chain, mode in rules.items():
            if not BASIC_SEL_CHAIN_PATTERN.match(sel_chain):
                raise FormalExcep('Malformed selector: %s' % sel_chain)
            selectors = sel_chain.split()
            indices = {}
            if self.matchRule(selectors, path, indices):
                if callable(mode):
                    arg_names = inspect.getfullargspec(mode).args
                    args = [indices.get(a) for a in arg_names]
                    mode = mode(*args)
                return mode
        return None

    def matchRule(self, selectors, path, indices, deferOnFail=False):
        """
        :param selectors: list of selectors remaining to be matched.
        :param path: ExpressionPath leading to this node.
        :param indices: a dictionary to be updated in-place with any indices
            matched in path segments.
        :param deferOnFail: this says what to do if we don't match: if True,
            ask parent node to make the same match; if False, just give up.

        :return: boolean saying whether we matched the rule or not.

        Selector formats:

            #id: match the id of the element

            type: match the "type" of the element, where "type" means the
                class name WITHOUT the leading "Formal".
                For example, use `Sum` to match any FormalSum object.

            @path: match the path of the element

                * path is absolute if selector comes first in the rule;
                  otherwise, path is relative to path of element matching
                  preceding selector.

                * Use bracket notation to match paths with indices.
                  E.g.
                        `term[i]-factor[j]`
                  will match
                        `term3-factor2`

                * When using bracket notation, use lambda abstraction when
                  defining the mode, using same variable names from the brackets.

                  Continuing the example above, could use

                    lambda i, j: {
                        'alpha': i + j
                    }

                  to substitute the sum of indices i and j for the value of a
                  formal variable of id 'alpha'.
        """
        sel = selectors.pop()
        defer = True
        next_path = None
        if sel[0] == "#":
            # id
            match = (self.id() == sel[1:])
        elif sel[0] == "@":
            # path
            pm = PathMatch(sel[1:], path)
            match = pm.matched
            if match:
                indices.update(pm.indices)
                next_path = pm.exp_path_prefix
                defer = False
        else:
            # type
            t = self.__class__.__name__
            if t.startswith('Formal'): t = t[6:]
            match = (t == sel)

        if not match:
            selectors.append(sel)

        if next_path is None:
            next_path = path[:]

        if (selectors and match) or (deferOnFail and not match):
            if next_path:
                ancestor, role = next_path.pop()
                return ancestor.matchRule(selectors, next_path, indices, deferOnFail=defer)
            else:
                return False
        else:
            return match

    def fwd(self, obj, role, rules, path, modifier=None, mode=None):
        """
        This is a convenience method with which to run a subobject's own
        format method and return the output.

        Given our expression path, plus the string naming the subobject's role,
        we assemble the subobject's expression path, and forward other relevant args.
        """
        if path is None: path = ExpressionPath()
        path += ExpressionPath(parent=self, role=role)
        return obj.format(mode=mode, rules=rules, path=path, modifier=modifier)

    def tryfwd(self, obj, role, rules, path, modifier=None, mode=None, mathmode=True):
        """
        Convenience method for forwarding when possible, else defaulting to
        mere string formatting.

        mathmode: Here you can say whether, in the case that the object is not
            a Formal subclass and must be converted to a string, it should be
            considered as being in math mode.

        All other parameters are as in the `fwd` method.
        """
        if isinstance(obj, Formal):
            return self.fwd(obj, role, rules, path, modifier=modifier, mode=mode)
        elif mathmode:
            return MM(obj)
        else:
            return str(obj)

    def getFwdMode(self, obj, role, rules, path, modifier=None, mode=None):
        """
        Return the mode that would be used by obj if we called `fwd` with the same args.
        """
        if path is None: path = ExpressionPath()
        path += ExpressionPath(parent=self, role=role)
        return obj.decideMode(mode=mode, rules=rules, path=path, modifier=modifier)

    ##########################################################################
    # Combining Operators

    def _(self, other):
        """
        Subscript
        """
        from stylgebra.expressions import FormalSubscripted
        other = wrap(other)
        return FormalSubscripted(self, other)

    def sub(self, other):
        """
        Alternative subscript, for symmetry with `sup`.
        """
        return self._(other)

    def __xor__(self, other):
        """
        Superscript
        """
        from stylgebra.expressions import FormalSuperscripted
        other = wrap(other)
        return FormalSuperscripted(self, other)

    def sup(self, other):
        """
        Alternative superscript
        """
        return self.__xor__(other)

    def __pow__(self, power, modulo=None):
        """
        Power
        """
        from stylgebra.expressions import FormalPower
        power = wrap(power)
        return FormalPower(self, power)

    def __neg__(self):
        from stylgebra.expressions import FormalSummand
        return -FormalSummand(self)

    def __add__(self, other):
        from stylgebra.expressions import FormalSummand
        other = wrap(other)
        return FormalSummand(self) + other

    def __sub__(self, other):
        from stylgebra.expressions import FormalSummand
        other = wrap(other)
        return FormalSummand(self) - other

    def __radd__(self, other):
        from stylgebra.expressions import FormalSummand
        other = wrap(other)
        return other + FormalSummand(self)

    def __rsub__(self, other):
        from stylgebra.expressions import FormalSummand
        other = wrap(other)
        return other - FormalSummand(self)

    def __mul__(self, other):
        from stylgebra.expressions import FormalProduct
        other = wrap(other)
        return FormalProduct([self, other])

    def __rmul__(self, other):
        other = wrap(other)
        from stylgebra.expressions import FormalProduct
        return FormalProduct([other, self])

    # Quotients for Python 2.x:
    def __div__(self, other):
        from stylgebra.expressions import FormalQuotient
        other = wrap(other)
        return FormalQuotient(self, other)

    def __rdiv__(self, other):
        from stylgebra.expressions import FormalQuotient
        other = wrap(other)
        return FormalQuotient(other, self)

    # Quotients for Python 3.x:
    def __truediv__(self, other):
        from stylgebra.expressions import FormalQuotient
        other = wrap(other)
        return FormalQuotient(self, other)

    def __rtruediv__(self, other):
        from stylgebra.expressions import FormalQuotient
        other = wrap(other)
        return FormalQuotient(other, self)


def withmode(format_method):
    """
    This function serves as a decorator for the `format` method of `Formal`
    subclasses. It serves to compute the mode, using the `decideMode` method,
    saving us from having to do that manually. In other words,

        @withmode
        def format(self, mode=None, rules=None, path=None, modifier=None):
            ...

    is the same as

        def format(self, mode=None, rules=None, path=None, modifier=None):
            mode = self.decideMode(mode, rules, path, modifier)
            ...

    It takes the same number of lines, but it is less tedious.
    """
    def f(formal_obj, mode=None, rules=None, path=None, modifier=None):
        mode = formal_obj.decideMode(mode, rules, path, modifier)
        return format_method(formal_obj, mode, rules, path, modifier)
    return f


class Infix:
    """
    This is a clever hack, thanks to
        <http://code.activestate.com/recipes/384122-infix-operators/>
    for turning any binary function into an infix operator.

    Given
        foo = lambda a, b: ...
    we can set
        infoo = Infix(foo)
    and then we will have
        a |infoo| b == foo(a, b)
    """
    
    def __init__(self, function):
        self.function = function
    
    def __ror__(self, other):
        return Infix(lambda x: self.function(other, x))
    
    def __or__(self, other):
        return self.function(other)
