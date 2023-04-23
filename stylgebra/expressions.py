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


import fractions

from sympy import isprime

from stylgebra.basic import *


class StrFormatArgs:
    """
    Instances of this class may serve as the `mode` argument when
    formatting a `FormalString`.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class FormalString(Formal):

    def __init__(self, s, mathmode=True):
        super().__init__()
        self.mathmode = mathmode
        self.s = MM(s) if mathmode else s

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        if isinstance(mode, StrFormatArgs):
            s = self.s.format(*mode.args, **mode.kwargs)
            return MM(s) if self.mathmode else s
        else:
            return self.s


class FormalVariable(Formal):

    def __init__(self, name, id=None):
        mode = name
        super().__init__(name=name, id=id, mode=mode)

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        r"""
        In the FormalVariable class, the mode plays an unusual role, in that
        it is used in order to substitute another object for the variable.

        Furthermore, if the substituted object is a Formal instance, then
        the variable takes on that object's value as its own; otherwise the
        variable takes on the object itself as its value.

        There are two ways to make the substitution:

        (1) The simplest way is to just pass the desired substitution itself as
        the mode.

        Then the substituted object can be addressed for formatting via the role
        of 'subst' relative to the variable. For example:

            i = FormalVariable('i')
            p = FormalInteger(7, 'p')

            i.format(p, {
                '#i @subst': {
                    'form': 'value'
                }
            })

        substitutes integer p for variable i, and then uses an ordinary rule
        dictionary to ask that p be printed by value.

        (2) Alternatively, you may pass a mode dict of the form

            {
                'subst': the thing to substitute,
                other key-value pairs to format the substituted thing...
            }

        When you use this format, the value under the key 'subst' is substituted for
        the variable, while the remainder of the mode dict is used as the _modifier_
        for the subst's mode. (Effectively, this means it will _be_ the subst's mode,
        unless you also address it directly via `@subst`, in which case the modifier
        will override.)

        Thus, our first example could also have been done this way,

            i.format({
                'subst': p,
                'form': 'value'
            })

        instead.
        """
        if isinstance(mode, dict) and 'subst' in mode:
            subst = mode['subst']
            subst_modifier = mode.copy()
            del subst_modifier['subst']
        else:
            subst = mode
            subst_modifier = None

        if isinstance(subst, Formal):
            self.value(subst.value())
        else:
            self.value(subst)

        return self.tryfwd(subst, 'subst', rules, path, modifier=subst_modifier, mathmode=True)


class FormalLookup(Formal):
    """
    This class can be thought of as a counterpart to the FormalMapping class.

    While the latter is meant to support writing down functions the way we typically
    do in mathematics, but is relatively weak in the types of function it can
    express via its `value_form` argument (which must be a Formal instance),
    the FormalLookup class is instead intended to support things like setting
    numerical coefficients for a polynomial, and is powerful in that you may
    pass any computable function, written in Python, as its `lookup`.

    Like the FormalMapping, however, the FormalLookup does read its inputs
    from Formal arguments.
    """

    def __init__(self, args, lookup, name=None, id=None):
        """
        args: a list of Formal objects (or a single Formal object), representing the
            argument(s) of the function
        lookup: either a callable, or a(n) (nested set of) array(s)/dict(s), in which to
            look up a value, based on the current values of the args. If callable, arity
            should match length of args list.
        """
        super().__init__(name=name, id=id)
        self.args = args if isinstance(args, list) else [args]
        self.lookup = lookup

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        We make no use of our own mode, but our computed value may be addressed
        under the path extension `-value`, if it requires its own formatting.
        (Compare FormalVariable's `-subst` path extension.)
        """
        # Typically there may be FormalVariables (nested) among our args, and these
        # set their value during their format call, so we do need to recurse, but we
        # do not need the return values.
        for i, arg in enumerate(self.args):
            self.fwd(arg, 'arg%d' % i, rules, path)
        # Now we can compute our value, based on theirs.
        f = self.lookup
        if callable(f):
            # If f is callable, we expect its arity to match our number of args.
            v = f(*[a.value() for a in self.args])
        else:
            # Otherwise f should be indexable, and so should its values, and so
            # on, until we have exhausted all our args.
            for a in self.args:
                j = a.value()
                try:
                    f = f[j]
                except IndexError:
                    raise FormalExcep(f'Index {j} not in lookup: {f}')
            v = f
        self.value(v)
        return self.tryfwd(v, 'value', rules, path, mathmode=True)


class FormalInteger(Formal):

    def __init__(
            self, value=None, name=None, id=None,
            pos=None, odd=None, prime=None
    ):
        # Unlike so many cases where we do want built-in int's wrapped
        # as FormalIntegers, in the case of a FormalInteger itself, we
        # want its value to be a built-in int. So in case a FormalInteger
        # was passed, we dig down until we hit rock-bottom.
        while isinstance(value, FormalInteger):
            value = value.value()
        super().__init__(value=value, name=name, id=id)
        if value is None:
            self.pos = pos
            self.odd = odd
            self.prime = prime
        else:
            self.pos = value > 0
            self.odd = value % 2 == 1
            self.prime = isprime(value)

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        mode options:

            form: FormOpt
                If undefined, behavior depends on what we have available:
                If we have a name, we use that; if not, then if we have a value,
                we use that; if not, then finally we use a verbal description.

            ordinal: boolean
                Default: False
                If form is _not_ 'verbal', and ordinal is True, then we will
                try to put the right ordinal suffix as a superscript.
        """

        form = mode.get('form')
        if form is None:
            if self.name() is not None:
                form = FormOpt.NAME
            elif self.value() is not None:
                form = FormOpt.VALUE
            else:
                form = FormOpt.VERBAL

        if form == FormOpt.NAME:
            s = MM(self.name())
        elif form in FormOpt.valsym:
            s = MM(self.value())
        else:
            assert form == FormOpt.VERBAL
            s = self.verbal()

        if mode.get('ordinal', False) and form != FormOpt.VERBAL:
            suffix = 'th'
            # The second condition here is so that we get 11th, 12th, 13th,
            # but 21st, 22nd, 23rd, etc.
            if s[-1:] in '123' and s[-2:-1] != '1':
                suffix = {
                    '1': 'st', '2': 'nd', '3': 'rd'
                }[s[-1:]]
            s = MM(r'%s^{\mathrm{%s}}' % (s, suffix))

        return s

    def verbal(self):
        adj_list = []

        if self.odd:
            adj_list.append('odd')
        elif self.odd is not None:
            adj_list.append('even')

        if self.pos:
            adj_list.append('positive')
        elif self.pos is not None:
            adj_list.append('negative')

        adjectives = ', '.join(adj_list)

        if self.prime:
            noun_phrase = 'prime'
        elif self.prime is not None:
            noun_phrase = 'composite integer'
        else:
            noun_phrase = 'integer'

        to_quantify = ''
        to_quantify += adjectives
        to_quantify += ' ' + noun_phrase
        to_quantify = to_quantify.strip()

        indef_art = 'a'

        if to_quantify[0] in 'aeiou':
            indef_art += 'n'

        d = indef_art + ' ' + to_quantify
        d = d.strip()

        return d


class FormalSubscripted(Formal):

    def __init__(self, base, sub, name=None, id=None):
        super().__init__(name=name, id=id)
        self.base = wrap(base)
        self.sub = wrap(sub)

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        We make no use of our own mode.

        subpath names:
            'base': self.base
            'sub':  self.sub
        """
        b = self.fwd(self.base, 'base', rules, path)
        s = self.fwd(self.sub, 'sub', rules, path)
        return MM(r'%s_{%s}' % (b, s))


class FormalSuperscripted(Formal):
    """
    A FormalSuperscripted is different from a FormalPower in that it really
    _just_ means that something will be written as a superscript; it does not
    involve any of the special rules that come into play when the superscript
    means a power (like writing a**0 as 1 or a**1 as a). See FormalPower class.
    """

    def __init__(self, base, sup, name=None, id=None):
        super().__init__(name=name, id=id)
        self.base = wrap(base)
        self.sup = wrap(sup)

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        We make no use of our own mode.

        subpath names:
            'base': self.base
            'sup':  self.sup
        """
        b = self.fwd(self.base, 'base', rules, path)
        s = self.fwd(self.sup, 'sup', rules, path)
        return MM(r'%s^{%s}' % (b, s))


class FormalPower(Formal):

    def __init__(self, base, power, name=None, id=None):
        super().__init__(name=name, id=id)
        self.base = wrap(base)
        self.power = wrap(power)

    def value(self):
        b = self.base.value()
        p = self.power.value()
        return b ** p

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        mode options:

            form: FormOpt
                Default: symbolic

            show-zero: True/False
                Default: False
                If True, write b^0; if False, write 1.

            show-unity: True/False
                Default: False
                If True, write b^1; if False, write b.

            negative: [ 'sup', 'frac', 'inline', 'inline-paren' ]
                Default: 'sup'
                This controls how we handle negative powers.
                'sup': write as superscript, just like any other power.
                'frac': write as \frac{1}{x}
                'inline': write as 1/x
                'inline-paren': write as 1/(x)

            brackets-base: [ 'auto', 'none', 'round', 'square', 'curly' ]
                Default: 'auto'
                Control how the base is bracketed.
                'auto': we try to detect when brackets are needed, and apply them
                    accordingly.
                Otherwise as usual.

            brackets-power: [ 'auto', 'none', 'round', 'square', 'curly' ]
                Default: 'auto'
                Like brackets-base, but for the exponent.

        subpath names:
            'base':  self.base
            'power': self.power
        """
        b = self.fwd(self.base, 'base', rules, path)
        p = self.fwd(self.power, 'power', rules, path)

        # Note: Generally, when we want to return the value, we must only do
        # this _after_ forwarding the format operation to all our subterms.
        #
        # You might think this was unnecessary in such a case; however, FormalVariables
        # take on their values during their format call. So we need to cascade through
        # all the format calls below us, in order to ensure that every object has the
        # value it is supposed to have.
        #
        # You will see this pattern repeated in many classes in this module.

        form = mode.get('form', FormOpt.SYMBOLIC)
        if form == FormOpt.NAME:
            return MM(self.name())
        if form == FormOpt.VALUE:
            return MM(str(self.value()))

        outer_form = '%s'
        negative_policy = mode.get('negative', 'sup')
        if p[0] == '-' and negative_policy != 'sup':
            outer_form = {
                'frac': r'\frac{1}{%s}',
                'inline': '1/%s',
                'inline-paren': r'1/\left(%s\right)',
            }.get(negative_policy, outer_form)
            p = negate_string(p)

        show_zero = mode.get('show-zero', False)
        show_unity = mode.get('show-unity', False)

        base_brack = mode.get('brackets-base', 'auto')
        power_brack = mode.get('brackets-power', 'auto')

        def should_auto_bracket_base():
            if p == '1' and not show_unity:
                return False
            should_bracket = False
            should_bracket |= is_proper_sum(self.base)
            # FIXME:
            #  This next test really needs to be more nuanced. We want to check
            #  whether the quotient actually has appeared _as_ a quotient after
            #  formatting. Did its denominator disappear? If so then maybe don't
            #  need the brackets.
            should_bracket |= isinstance(self.base, FormalQuotient)
            return should_bracket

        if base_brack == 'auto':
            if should_auto_bracket_base():
                base_brack = 'round'

        if power_brack == 'auto' and is_proper_sum(self.power): power_brack = 'round'

        b = bracket_expression(base_brack, b)
        p = bracket_expression(power_brack, p)

        if p == '0' and not show_zero:
            return MM('1')
        elif p == '1' and not show_unity:
            return MM(outer_form % b)
        else:
            x = '%s^{%s}' % (b, p)
            return MM(outer_form % x)


class FormalSet(Formal):

    def __init__(self, elements, condition=None, name=None, id=None):
        """
        :param elements: either a list of formal elements, or a single formal element
        :param condition: optional formula satisfied by the elements
        """
        if not isinstance(elements, list):
            elements = [elements]
        elements = [wrap(e) for e in elements]
        self.elements = elements

        self.condition = condition
        Formal.__init__(self, name=name, id=id)

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        r"""
        mode options:

            form: FormOpt
                Default: symbolic

            empty: [ 'slashzero', 'braces' ]
                Say how empty set should be displayed.
                Default: 'slashzero'
                'slashzero': \varnothing
                'braces': \{\}

            cond: [ 'colon', 'vbar', 'where', 'with' ]
                Say how the condition should be displayed.
                Default: 'colon'
                'colon': after a colon (:) inside the braces
                'vbar': after a vertical bar (|) inside the braces
                'where': after the word "where" outside the braces
                'with': after the word "with" outside the braces

        subpaths:

            'elt%d' % i: self.elements[i]
            'cond': self.condition
        """

        elt_strings = [
            self.fwd(elt, 'elt%d' % i, rules, path, modifier)
            for i, elt in enumerate(self.elements)
        ]

        cond_string = self.fwd(self.condition, 'cond', rules, path) if self.condition is not None else None

        form = mode.get('form', FormOpt.SYMBOLIC)

        if form == FormOpt.NAME:
            return MM(self.name())
        elif form == FormOpt.VALUE:
            # Q: What could this actually mean? For now just leave it...
            return MM(self.value())
        elif form == FormOpt.VERBAL:
            return self.verbal(elt_strings, cond_string)

        assert form == FormOpt.SYMBOLIC

        n = len(self.elements)
        if n == 0:
            # Empty set
            empty_style = mode.get('empty', 'slashzero')
            if empty_style == 'braces':
                return MM(r'\{\}')
            else:
                return MM(r'\varnothing')

        elt_list = MM(', ').join(elt_strings)
        inner_cond = ''
        outer_cond = ''

        if cond_string is not None:
            cond_style = mode.get('cond', 'colon')
            if cond_style == 'colon':
                inner_cond = MM(' : ') + mbox(cond_string)
            elif cond_style == 'vbar':
                inner_cond = MM(r' \mid ') + mbox(cond_string)
            elif cond_style == 'where':
                outer_cond = ' where ' + cond_string
            elif cond_style == 'with':
                outer_cond = ' with ' + cond_string

        s = MM(r'\left\{ ') + elt_list + inner_cond + MM(r' \right\}') + outer_cond
        return s

    def verbal(self, elt_strings, cond_string=None):
        n = len(self.elements)
        if n == 0:
            s = 'the empty set'
        elif n > 1:
            s = 'the set containing ' + ', '.join(elt_strings)
        else:
            s = 'the set of all ' + elt_strings[0]
            if cond_string is not None:
                s += ' such that ' + cond_string
        return s


class FormalMapping(Formal):

    def __init__(self, name_form=None, domain=None, codomain=None, args=None, value_form=None, name=None, id=None):
        r"""
        name_form: a Formal object representing the name of the mapping
        domain: a Formal object representing the domain of the mapping
        codomain: a Formal object representing the codomain of the mapping
        args: a list of Formal objects, representing the argument(s) of the function
        value_form: a Formal object to represent the value of this mapping; generally,
            should involve the argument forms in one way or another.

        Example:
            sig = FormalString(r'\sigma')
            i = FormalVariable('i')
            p = FormalInteger('p', 11)
            F = CyclotomicField(p)
            zeta = FormalVariable('zeta', r'\zeta')

            sig_i = FormalMapping(sig._(i), F, F, [zeta], zeta**i, 'sig_i')

        """
        super().__init__(name=name, id=id)
        self.name_form = name_form
        self.domain = domain
        self.codomain = codomain
        self.args = args or []
        self.value_form = value_form

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        mode options:

            form: [ 'name', 'name-args', 'value', 'map', 'mapsto', 'name-mapsto' ]
                Default: 'name'
                'name':         f
                'name-args':    f(args)
                'value':        value
                'map':          f: D --> C
                'mapsto':       args |--> value
                'name-mapsto':  f: args |--> value

        subpath names:
            'name':      self.name_form
            'arg%d' % i: self.args[i]
            'value':     self.value_form
            'domain':    self.domain
            'codomain':  self.codomain
        """
        form = mode.get('form', 'name')

        f, a, v, D, C = None, None, None, None, None
        if form not in ['value', 'mapsto']:
            f = self.fwd(self.name_form, 'name', rules, path)
        if form in ['name-args', 'mapsto', 'name-mapsto']:
            a = MM(', ').join([
                self.fwd(self.args[i], 'arg%d' % i, rules, path) for i in range(len(self.args))
            ])
        if form in ['value', 'mapsto', 'name-mapsto']:
            v = self.fwd(self.value_form, 'value', rules, path)
        if form == 'map':
            D = self.fwd(self.domain, 'domain', rules, path)
            C = self.fwd(self.codomain, 'codomain', rules, path)

        if form == 'name':
            return f
        elif form == 'name-args':
            return MM('%s(%s)' % (f, a))
        elif form == 'value':
            return v
        elif form == 'map':
            return MM(r'%s: %s \rightarrow %s' % (f, D, C))
        elif form == 'mapsto':
            return MM(r'%s \mapsto %s' % (a, v))
        elif form == 'name-mapsto':
            return MM(r'%s: %s \mapsto %s' % (f, a, v))


class FormalEllipsis(Formal):

    def __init__(self):
        super().__init__()

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        mode options:

            style: [ 'l', 'c', 'v' ]
                Default: 'l'
                'l': ldots
                'c': cdots
                'v': vdots
        """
        s = mode.get('style', 'l')
        assert s in 'lcv'
        return MM('\\' + s + 'dots')


# We provide one general-purpose instance of the FormalEllipsis class,
# under a name that looks a bit like "...". The idea is that anyone can
# use this as a convenience when they need an ellipsis.
ooo = FormalEllipsis()


def is_ellipsis(thing):
    return thing == Ellipsis or isinstance(thing, FormalEllipsis)


class FormalInfinity(Formal):

    def __init__(self, sign=1, name=None, id=None):
        super().__init__(name=name, id=id)
        self.sign = sign

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        sign = MM('-') if self.sign == -1 else ''
        return sign + MM(r'\infty')


def negate_string(s):
    """
    Simple method of formally negating a string expression:
    If it begins with a '-', take that away; else add one.
    """
    if s[:1] == '-':
        s = MM(s[1:])
    else:
        s = MM('-') + s
    return s


class FormalSummand(Formal):

    def __init__(self, term, sign=1):
        super().__init__()
        self.term = wrap(term)
        self.sign = sign

    def value(self):
        return self.sign * self.term.value()

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        Only one mode of operation. If sign is +1, we return our term's format result.
        If sign is -1, we try to ask our term to negate itself, and return the format
        result for the resulting term; if that cannot be done, we just tack a '-' sign
        onto the front of our term's format result, or try to take one away.

        submode names:
            'term': self.term
        """
        s = self.fwd(self.term, 'term', rules, path)
        if self.sign == -1:
            s = negate_string(s)
        return s

    def __neg__(self):
        return FormalSummand(self.term, -self.sign)

    def __add__(self, other):
        if isinstance(other, FormalSummand):
            return FormalSum([self, other])
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, FormalSummand):
            return FormalSum([self, -other])
        return NotImplemented


class MultiOp:
    """
    Mixin for "multi-operand" classes like FormalSum and FormalProduct.
    """

    def __init__(self, items):
        self.items = items

    def __len__(self):
        return len(self.items)

    def make_flat_items(self):
        flat = []
        for item in self.items:
            if isinstance(item, self.__class__):
                fi = item.make_flat_items()
                flat.extend(fi)
            else:
                flat.append(item)
        return flat

    def flatten(self):
        """
        Flatten this object's items array.
        Modifies this object in-place.
        See also `flattened` method.
        """
        self.items = self.make_flat_items()

    def flattened(self):
        """
        Return a new object whose items array is a flattened
        version of this one's. This object is unaltered.
        See also `flatten` method.
        """
        return self.__class__(self.make_flat_items())

    def permute(self, perm):
        """
        Permute the items according to a permutation given in "all targets"
        format, i.e. by listing the target to which each index gets mapped,
        using 0-based indices.

        For example, for the permutation

                    (0 1 2 3)
                    (0 2 1 3)

        that simply transposes indices 1 and 2, you would pass [0, 2, 1, 3].
        """
        self.items = [self.items[perm[i]] for i in range(len(perm))]

    def permuted(self, perm):
        """
        Like the `permute` method, only this time return a new object, instead
        of changing this one in-place.
        """
        items = [self.items[perm[i]] for i in range(len(perm))]
        return self.__class__(items)

    def split(self, parts, alt_cls=None):
        """
        Split this multi into a multi of multis.

        :param parts: list of list of indices. Each list says which operands
          you want in that group, and in what order. So you can also achieve
          a permutation at the same time.

        :param alt_cls: "alternate class". If given, this class will be used
          as the outer multi, which has all the others as its items.

        Example:
            pr1 = FormalProduct([a, b, c, d]).flattened()
            pr2 = pr1.split([
                [0, 3], [2, 1]
            ])

            pr1.format()
            # a b c d

            pr2.format()
            # (a d)(c b)
        """
        inner_cls = self.__class__
        outer_cls = alt_cls or self.__class__
        multis = [
            inner_cls([self.items[i] for i in part])
            for part in parts
        ]
        return outer_cls(multis)


class FormalSum(Formal, MultiOp):

    def __init__(self, terms=None, name=None, id=None):
        """
        :param terms: list of terms to be summed. If a term is not already a
          FormalSummand, we will wrap it in one. If you want a term to be subtracted
          rather than added, then you need to wrap it as a FormalSummand yourself,
          and set the sign to -1.
        """
        terms = terms or []
        # Ensure that everything is wrapped in a FormalSummand
        summands = [
            t if isinstance(t, FormalSummand) else FormalSummand(t)
            for t in terms
        ]
        Formal.__init__(self, name=name, id=id)
        MultiOp.__init__(self, summands)

    def summands(self):
        return self.items

    def value(self):
        return sum([s.value() for s in self.summands()])

    def make_flat_items(self):
        """
        Due to special structure with each term being wrapped
        in a FormalSummand, and the possible need to negate,
        we need to override the superclass method.
        """
        flat = []
        for summand in self.summands():
            term = summand.term
            if isinstance(term, FormalSum):
                fs = term.make_flat_items()
                if summand.sign == -1:
                    flat.extend([-s for s in fs])
                else:
                    flat.extend(fs)
            else:
                flat.append(summand)
        return flat

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        mode options:

            form: FormOpt
                Default: symbolic

            brackets: [ 'none', 'round', 'square', 'curly' ]
                Default: 'none'
                Surround the entire expression with some kind of brackets.

            show-zeros: True/False
                Default: False
                If True, show terms equal to zero (0). If False, suppress these.

            flip-ops: True/False
                Default: True
                If True, flip operations +/- when the next term begins with a
                  minus sign '-'.

        subpath names:
            'term%d' % i: self.summands()[i].term
        """

        def make_modifier(term):
            if isinstance(term, FormalSum):
                # If the term is a sum, force it to be parenthesized.
                return {'brackets': 'round'}
            elif isinstance(term, FormalEllipsis):
                # Ellipses must be center-style
                return {'style': 'c'}
            else:
                return None

        term_strings = [
            self.fwd(summand.term, 'term%d' % i, rules, path, modifier=make_modifier(summand.term))
            for i, summand in enumerate(self.summands())
        ]

        form = mode.get('form', FormOpt.SYMBOLIC)
        if form == FormOpt.NAME:
            return MM(self.name())
        if form == FormOpt.VALUE:
            return MM(str(self.value()))

        s = ''
        first = True
        multiple_terms = False

        show_zeros = mode.get('show-zeros', False)
        flip_ops = mode.get('flip-ops', True)

        for f, summand in zip(term_strings, self.summands()):
            sign = summand.sign

            # Omit zeros if desired
            if f in ['0', '-0'] and not show_zeros: continue

            if first:
                first = False
                if sign == -1:
                    f = negate_string(f)
                s = f
            else:
                # Flip sign if appropriate
                if f[0] == '-' and flip_ops:
                    sign *= -1
                    f = MM(f[1:])

                op = {-1: '-', 1: "+"}[sign]
                s += MM(' %s %s' % (op, f))
                multiple_terms = True

        if s == '':
            # An empty sum equals zero.
            s = '0'

        bracket_style = mode.get('brackets', 'none')
        if multiple_terms and bracket_style != 'none':
            s = bracket_expression(bracket_style, s)

        return MM(s)


def is_proper_sum(obj):
    """
    Say whether a formal object appears to be a sum of at least two terms.
    This may be useful in judging whether an expression needs to be surrounded
    by brackets.
    """
    return isinstance(obj, FormalSum) and len(obj) >= 2


class FormalRangeBuilder(Formal):
    r"""
    Abstract base class for a variety of kinds of mathematical expressions, in which
    some "range" of terms or elements are assembled or combined in one way or another.

    In particular, this class supports styling options to spell out all the elements,
    or to instead express a condition on a bound variable.

    For example, this class will have a subclass to support the construction of sums,
    and one to support the construction of sets. Given the same initialization,

        rng = [0, 1, ..., p - 2]
        gen_form = a._{i}
        bound_var = i

    these subclasses could produce both spelled-out formats:

        sum:
            a_{0} + a_{1} + \ccc + a_{p - 2}

        set:
            \{ a_{0}, a_{1}, \ddd, a_{p - 2} \}

    or, with different styling options, bound formats:

        sum:
            \Sum_{i = 0}^{p - 2} a_i

        set:
            \{ a_i : 0 \leq i \leq p - 2 \}
    """

    def __init__(self, rng=None, gen_form=None, bound_var=None, cond=None, name=None, id=None):
        """
        rng: the "range", i.e. a list indicating the range of terms or elements
            involved in the construction. May include ellipses.
        gen_form: a Formal object representing the generic form of an element.
        bound_var: a FormalVariable representing the bound variable over which
            the range extends. Should occur at least once in the gen_form.

        If gen_form and bound_var are defined then the range is interpreted as
        a list of values that are to be substituted for the bound variable.
        If they are not both defined, then the range is interpreted as the list
        of desired terms or elements themselves.
        """
        super().__init__(name=name, id=id)
        self.range = rng or []
        if gen_form is None or bound_var is None:
            bound_var = FormalVariable('i')
            # Somewhat hacky: since we will be addressing var i with a selector that expects
            # to find it strictly _within_ the generic term, we can't just make the
            # latter equal to i; we have to put i within it.
            gen_form = FormalVariable('j')
            gen_form.mode(bound_var)
        self.gen_form = gen_form
        self.bound_var = bound_var
        self.cond = cond

        # Instead of overriding the make_subst_rules method, subclasses may opt
        # to simply define an item_subpath_name, and let the generic method do
        # the rest. For many (if not all) subclasses, this will suffice.
        # For example, the `FormalRangeSum` class need only set item_subpath_name
        # equal to `term`; the `FormalRangeSet` class need only set it equal
        # to `elt`.
        self.item_subpath_name = None

    def make_subst_rules(self, basepath):
        if self.item_subpath_name is None:
            raise NotImplementedError()
        if basepath: basepath += '-'
        rule = f'@{basepath}{self.item_subpath_name}[i] #{self.bound_var.id()}'
        return {
            rule: lambda i: self.range[i],
        }

    def interpolate_range(self, step_size):
        if len(self.range) == 2 and step_size != 0:
            # I suppose the endpts need to be FormalIntegers.
            # But our task is actually quite tricky since even if an endpt has
            # a numerical value, the question of whether we want an ellipsis is
            # really the question of how we want the endpt to be displayed, i.e.
            # by name or by value. So we need to do some kind of formatting lookahead
            # and check which mode is going to be applied (NAME or VALUE or other)
            # to the FormalInteger in question.
            ...  # TODO
            raise NotImplementedError("range interpolation feature not supported yet")
        else:
            return self.range[:]

    def build_subobject_for_list(self, items):
        """
        Subclasses must override.
        """
        raise NotImplementedError()

    def bound_format_with_range_bounds(self, a, b, mode, rules, path, modifier):
        """
        Subclasses must override.
        Produce the desired formatting where the condition on the bound variable
        is that it lie in the range from a to b.

        a: lower bound for range
        b: upper bound for range

        Other parameters are as in the `format` method.

        :return: string
        """
        raise NotImplementedError()

    def bound_format_with_generic_condition(self, cond, mode, rules, path, modifier):
        """
        Subclasses must override.
        Produce the desired formatting where the condition on the bound variable
        is a generic one.

        cond: the condition on the bound variable.

        Other parameters are as in the `format` method.

        :return: string
        """
        raise NotImplementedError()

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        r"""
        options:

            range: [ 'auto', 'list', 'bind' ]
                Default: auto
                list: write out all the elements, making substitutions from the range
                    into the gen_form through the bound_var.
                bind: express the gen_form as is, together with conditions on the bound_var.
                    Unless condition was explicitly given, assume it is boundedness by the
                    first and last elements of the range. Interpret the latter as -/+ \infty
                    if they are ellipses.
                auto: choose behavior based on length n of the range. If n >= 3 then operate
                    in list mode; if n == 2, then operate in bind mode if step option (see
                    below) is zero, otherwise list mode; if n == 1 operate in bind mode but
                    do not infer any condition from the range.

                In all cases, if the range is of length 0 then behavior is controlled by the
                subclass. E.g. empty sums should be '0', empty products should be '1', etc.

            step: int
                Default: 0
                step is only relevant if mode is 'list' and the range is length 2.
                Then step == 0 means do not fill in any additional items.
                Otherwise fill in additional items according to the step size.
                If either endpt of the range is non-numerical then use an ellipsis.

        """
        range_mode = mode.get('range', 'auto')
        step_size = mode.get('step', 0)
        try: step_size = int(step_size)
        except ValueError: raise FormalExcep(f'Malformed step size "{step_size}". Should be integer.')
        len_range = len(self.range)
        if range_mode == 'auto':
            if len_range >= 3:
                range_mode = 'list'
            elif step_size != 0:
                range_mode = 'list'
            else:
                range_mode = 'bind'

        if range_mode == 'list':
            #range_ = self.interpolate_range(step_size)
            range_ = self.range[:]
            rules = rules or {}
            path = path or ExpressionPath()
            basepath = path.rolepath()
            subst_rules = self.make_subst_rules(basepath)
            items = [
                ooo if is_ellipsis(a) else self.gen_form
                for a in range_
            ]
            subobject = self.build_subobject_for_list(items)
            assert isinstance(subobject, Formal)
            rules.update(subst_rules)
            return subobject.format(mode, rules, path, modifier)

        else:
            assert range_mode == 'bind'
            if self.cond is None and len_range >= 2:
                a = self.range[0]
                b = self.range[-1]
                a = FormalInfinity(sign=-1) if is_ellipsis(a) else wrap(a)
                b = FormalInfinity(sign=1) if is_ellipsis(b) else wrap(b)
                return self.bound_format_with_range_bounds(a, b, mode, rules, path, modifier)
            else:
                if self.cond is None and isinstance(self, FormalRangeOperator):
                    self.cond = self.bound_var
                return self.bound_format_with_generic_condition(self.cond, mode, rules, path, modifier)


class FormalRangeSet(FormalRangeBuilder):

    def __init__(self, rng=None, gen_form=None, bound_var=None, cond=None, name=None, id=None):
        super().__init__(rng, gen_form, bound_var, cond, name, id)
        self.item_subpath_name = 'elt'

    def build_subobject_for_list(self, items):
        return FormalSet(items, condition=self.cond)

    def bound_format_with_generic_condition(self, cond, mode, rules, path, modifier):
        S = FormalSet([self.gen_form], condition=cond)
        return S.format(mode, rules, path, modifier)

    def bound_format_with_range_bounds(self, a, b, mode, rules, path, modifier):
        from stylgebra.relations import lt, leq
        l_reln = lt if isinstance(a, FormalInfinity) else leq
        r_reln = lt if isinstance(b, FormalInfinity) else leq
        cond = a |l_reln| self.bound_var |r_reln| b
        return self.bound_format_with_generic_condition(cond, mode, rules, path, modifier)


class FormalRangeOperator(FormalRangeBuilder):
    """
    This abstract class unifies all those FormalRangeBuilders that work like
    Sum or Product, in the way they express bound format, be it for a range
    of indices, or a generic condition.
    """

    def __init__(self, rng=None, gen_form=None, bound_var=None, cond=None, name=None, id=None):
        super().__init__(rng, gen_form, bound_var, cond, name, id)
        # Subclasses must define their operator symbol.
        # E.g. r'\sum', r'\prod', etc.
        self.operator_symbol = None

    def build_subobject_for_list(self, items):
        """
        Subclasses must override.
        """
        raise NotImplementedError()

    def bound_format_with_range_bounds(self, a, b, mode, rules, path, modifier):
        """
        subpaths:
            form: self.gen_form
            var: self.bound_var
            lower: a
            upper: b
        """
        # TODO:
        #   Maybe use more sophisticated TeX?
        #   See: <https://tex.stackexchange.com/a/85072>
        #        <https://www.overleaf.com/learn/latex/Integrals,_sums_and_limits>
        if self.operator_symbol is None:
            raise NotImplementedError()
        form = self.fwd(self.gen_form, 'form', rules, path)
        var = self.fwd(self.bound_var, 'var', rules, path)
        lower = self.fwd(a, 'lower', rules, path)
        upper = self.fwd(b, 'upper', rules, path)
        op = MM(self.operator_symbol)
        subscript = MM('_{') + var + MM(' = ') + lower + MM('}')
        superscript = MM('^{') + upper + MM('} ')
        return op + subscript + superscript + form

    def bound_format_with_generic_condition(self, cond, mode, rules, path, modifier):
        """
        subpaths:
            form: self.gen_form
            cond: cond
        """
        if self.operator_symbol is None:
            raise NotImplementedError()
        form = self.fwd(self.gen_form, 'form', rules, path)
        cond = self.fwd(cond, 'cond', rules, path)
        op = MM(self.operator_symbol)
        subscript = MM('_{') + cond + MM('} ')
        return op + subscript + form


class FormalRangeSum(FormalRangeOperator):

    def __init__(self, rng=None, gen_form=None, bound_var=None, cond=None, name=None, id=None):
        super().__init__(rng, gen_form, bound_var, cond, name, id)
        self.operator_symbol = r'\sum'
        self.item_subpath_name = 'term'

    def build_subobject_for_list(self, items):
        return sum(items, FormalSum()).flattened()

    def generic_term(self):
        return self.gen_form


class FormalRangeProd(FormalRangeOperator):

    def __init__(self, rng=None, gen_form=None, bound_var=None, cond=None, name=None, id=None):
        super().__init__(rng, gen_form, bound_var, cond, name, id)
        self.operator_symbol = r'\prod'
        self.item_subpath_name = 'factor'

    def build_subobject_for_list(self, items):
        return FormalProduct(factors=items)


"""
A word on the implementation differences between addition & subtraction on the
one hand, and multiplication & division on the other:

This module is supposed to help us model _common_ practice in mathematical
expression, of the kind you see in textbooks, and on chalkboards. And, whereas
it is common to see long chains of mixed adding and subtracting,

    a + b - c + d - e - f

it is in no way common to see similar chains of mixed multiplying and dividing
in such contexts:

    a * b / c * d / e / f

This is why, while it seemed suitable to use a FormalSummand class, with a
positive and negative modality, in order to model the former (in combination
with the FormalSum class), we do _not_ plan to have an analogous "FormalFactor"
class.

Instead, a FormalProduct and FormalQuotient class should suffice to let us model
the common practice with multiplication & division, wherein we tend to have a
single quotient, with a product upstairs and a product downstairs, as in

    (a*b*d) / (c*e*f)

(If we were to do likewise with addition & subtraction then the sum above
would be gathered as (a + b + d) - (c + e + f). While certainly acceptable,
this is in no way required by convention.) 
"""


class FormalProduct(Formal, MultiOp):

    def __init__(self, factors=None, name=None, id=None):
        Formal.__init__(self, name=name, id=id)
        factors = [wrap(f) for f in factors]
        MultiOp.__init__(self, factors or [])

    def factors(self):
        return self.items

    def value(self):
        v = 1
        for f in self.factors():
            v *= f.value()
        return v

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        mode options:

            form: FormOpt
                Default: symbolic

            brackets: [ 'none', 'round', 'square', 'curly' ]
                Default: 'none'
                Surround the entire expression with some kind of brackets.

            collapse-zero: True/False
                Default: True
                If True, and if any factor looks like zero, then return '0' for the
                  entire product.
                If False, include zeros just like any other factor.

            mult-symb: [ 'none', 'dot', 'x', 'paren' ]
                Default: 'none'
                Say what multiplication symbol you want to appear between (or around) factors.

            numerals: [ 'front-dot', 'dot', 'none' ]
                Default: 'front-dot'
                Say how to handle numeral factors.
                At present the set of factors regarded as "numerals" is quite limited: their
                    string representation has to parse as an integer. We may expand this in
                    future versions.
                'dot': if 'mult-symb' is 'none', then put a cdot before any numeral
                    (except for the leftmost factor in the entire product).
                'front-dot': like 'dot', plus bring numerals to the front (left side)
                    of the product.
                'none': no special processing for numerals.

            show-unity: True/False
                Default: False
                If True, show factors equal to unity (1). If False, suppress these.

            signs: [ 'gather', 'bracket', 'auto' ]
                Default: 'gather'
                Say how to treat factors whose expression begins with a minus sign '-'.
                'gather': Negations are counted up, and at most a single minus
                  sign will appear at the front of the whole product (according
                  to parity of the count), with all others suppressed.
                'bracket': All negated factors are bracketed.
                'auto': Negated factors are bracketed unless prefixed by some multiplication
                    symbol due to the `mult-symb` option or the `numerals` option.

        subpaths:
            'factor%d' % i: self.factors()[i]
        """

        def make_modifier(factor):
            if isinstance(factor, FormalSum):
                return {'brackets': 'round'}
            elif isinstance(factor, FormalProduct):
                return {'brackets': 'round'}
            elif isinstance(factor, FormalEllipsis):
                # Ellipses must be center-style
                return {'style': 'c'}
            else:
                return None

        factor_strings = [
            self.fwd(factor, 'factor%d' % i, rules, path, modifier=make_modifier(factor))
            for i, factor in enumerate(self.factors())
        ]

        form = mode.get('form', FormOpt.SYMBOLIC)
        if form == FormOpt.NAME:
            return MM(self.name())
        if form == FormOpt.VALUE:
            return MM(self.value())

        mult_symb_rule = mode.get('mult-symb', 'none')
        mult_symbol_str = MM({
            'none': ' ',
            'dot': r' \cdot ',
            'x': r' \times ',
            'paren': ')('
        }[mult_symb_rule])

        collapse_zero = mode.get('collapse-zero', True)
        show_unity = mode.get('show-unity', False)

        sign_rule = mode.get('signs', 'gather')
        gather_signs = sign_rule == 'gather'
        bracket_signs = sign_rule == 'bracket' or (sign_rule == 'auto' and mult_symbol_str == ' ')

        numeral_rule = mode.get('numerals', 'front-dot')
        gather_numerals = numeral_rule == 'front-dot'
        dot_numerals = (mult_symb_rule == 'none' and numeral_rule[-3:] == 'dot')

        pruned = []
        numerals = []
        num_neg = 0
        num_numerals = 0
        num_factors = 0
        for s in factor_strings:
            needs_brackets = False

            if s in ['0', '-0'] and collapse_zero:
                product = MM('0')
                break

            if s[0] == '-':
                if gather_signs:
                    num_neg += 1
                    s = MM(s[1:])
                elif bracket_signs:
                    needs_brackets = True

            if s != '1' or show_unity:

                treat_as_numeral = False
                if gather_numerals or dot_numerals:
                    try: int(s)
                    except ValueError: pass
                    else: treat_as_numeral = True

                if dot_numerals and treat_as_numeral:
                    if num_numerals > 0 or (num_factors > 0 and not gather_numerals):
                        s = MM(r'\cdot ') + s
                        needs_brackets = False

                if needs_brackets:
                    s = MM('(') + s + MM(')')

                if gather_numerals and treat_as_numeral:
                    numerals.append(s)
                    num_numerals += 1
                else:
                    pruned.append(s)

                num_factors += 1
        else:
            # We didn't break, meaning either we never encountered a zero, or
            # we want to show zeros like regular factors.
            if gather_numerals:
                pruned = numerals + pruned
            sign = MM('-') if num_neg % 2 == 1 else ''
            term = MM('1') if num_factors == 0 else mult_symbol_str.join(pruned)
            if mult_symbol_str == ')(':
                term = MM("(") + term + MM(")")
            product = sign + term

        bracket_style = mode.get('brackets', 'none')
        product = bracket_expression(bracket_style, product)

        return MM(product)


def formalQuoFromFrac(frac):
    """
    Turn an instance of python's fractions.Fraction class into a FormalQuotient.
    """
    return FormalQuotient(frac.numerator, frac.denominator)


class FormalQuotient(Formal):

    def __init__(self, top, bot, name=None, id=None):
        super().__init__(name=name, id=id)
        self.top = wrap(top)
        self.bot = wrap(bot)

    def value(self):
        vt = self.top.value()
        vb = self.bot.value()
        if isinstance(vt, int) and isinstance(vb, int):
            vq = fractions.Fraction(vt, vb)
        else:
            vq = vt / vb
        return vq

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        mode options:

            form: FormOpt
                Default: symbolic

            inline: True/False
                Default: False
                If True, write as top/bot; if False, write as \frac{top}{bot}.

            brackets-top: [ 'none', 'round', 'square', 'curly' ]
                Default: 'none'
                Surround the entire top expression with some kind of brackets.

            brackets-bot: [ 'none', 'round', 'square', 'curly' ]
                Default: 'none'
                Surround the entire bottom expression with some kind of brackets.

            collapse-zero: True/False
                Default: True
                If True, and if the numerator looks like zero, then return '0' for the
                  entire quotient.

            sign-front: True/False
                Default: True
                If True, attempt to cancel signs in numerator and denominator, and bring
                    any remaining negation out in front of the expression.

            collapse-int: True/False
                Default: True
                If True, and if the denominator looks like unity, then just write the
                    numerator.

        subpaths:
            'top': self.top
            'bot': self.bot
        """
        t = self.fwd(self.top, 'top', rules, path)
        b = self.fwd(self.bot, 'bot', rules, path)

        form = mode.get('form', FormOpt.SYMBOLIC)
        if form == FormOpt.NAME:
            return MM(self.name())
        if form == FormOpt.VALUE:
            return MM(self.value())

        collapse_zero = mode.get('collapse-zero', True)
        sign_front = mode.get('sign-front', True)
        collapse_int = mode.get('collapse-int', True)

        if t in ['0', '-0'] and collapse_zero:
            return MM('0')

        num_neg = 0
        if sign_front:
            if t[0] == '-':
                num_neg += 1
                t = MM(t[1:])
            if b[0] == '-':
                num_neg += 1
                b = MM(b[1:])

        top_bracket_style = mode.get('brackets-top', 'none')
        bot_bracket_style = mode.get('brackets-bot', 'none')

        t = bracket_expression(top_bracket_style, t)
        b = bracket_expression(bot_bracket_style, b)

        if b == '1' and collapse_int:
            q = t
        elif mode.get('inline'):
            q = '%s/%s' % (t, b)
        else:
            q = r'\frac{%s}{%s}' % (t, b)

        if num_neg == 1:
            q = f'-{q}'

        return MM(q)

##############################################################################
# Tests

def try01():
    a = FormalInteger(1, 'a')
    b = FormalInteger(2, 'b')
    c = FormalInteger(0, 'c')

    s0 = a + b + c
    print(s0.format())

def try02():
    a = FormalVariable('a')
    b = FormalVariable('b')
    c = FormalVariable('c')
    d = FormalVariable('d')

    pr0 = a * b * c * d
    print(pr0.format())

def try03():
    end_pattern = 'cat-foo[i]bar[j]'
    paths = [
        'baz3-cat-foo17bar81',
        'cat-foo0bar1',
        'foo2bar3',
        'cat-foo5bar'
    ]
    for path in paths:
        print("="*50)
        print(path)
        R = path.split('-')
        A = [None] * len(R)
        ep = ExpressionPath(A, R)
        pm = PathMatch(end_pattern, ep)
        print(pm.matched)
        if pm.matched:
            print(pm.indices)
            print(pm.num_segments_matched)
            print(pm.rolepath_prefix)
            print(pm.exp_path_prefix)

def try04():
    zeta = FormalVariable(r'\zeta', 'zeta')
    g = FormalVariable('g')
    quo = (1 - zeta ** g) / (1 - zeta)
    s = quo.format({
        'brackets-top': 'round',
        'brackets-bot': 'round'
    }, {
        '#g': FormalProduct([3, 5]),
        # But it is easier to find it this way:
        '#g @subst': {
            'mult-symb': 'dot'
        }
    })
    print(s)

def try05():
    a = FormalString('a')
    i = FormalVariable('i')
    zeta = FormalVariable(r'\zeta', 'zeta')
    p = FormalInteger(11, 'p')
    alpha = FormalRangeSum([0, 1, ..., p - 2], a._(i) * zeta ** i, i)
    s = alpha.format()
    print(s)

def try06():
    b = FormalInteger(1)
    d = FormalInteger(3)
    q2 = (-b) / d
    s = q2.format()
    print(s)

def try07():
    x = FormalVariable('x')
    y = FormalVariable('y')
    a = FormalInteger(2)
    b = FormalInteger(-3)
    p1 = x * a * b * y
    p1.flatten()
    s = p1.format({
        'signs': 'auto'
    })
    print(s)

def try08():
    x = FormalVariable('x')
    a = FormalInteger(2, 'a')
    s1 = x.format(a, {
        '#x @subst': {
            'form': 'value'
        }
    })
    print(s1)
    s2 = x.format({
        'subst': a,
        'form': 'value'
    })
    print(s2)

def try09():
    from stylgebra.relations import in_
    p = FormalVariable('p')
    f = (1 - 1/p)**(-1)
    S = [2, 3, 5, 7]
    pr2 = FormalRangeProd([], gen_form=f, bound_var=p, cond=p |in_| S)
    s = pr2.format()
    print(s)

if __name__ == "__main__":
    try09()
