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


from sympy import primitive_root

from stylgebra.basic import *
from stylgebra.expressions import *
from stylgebra.relations import *
from stylgebra.numerical import nice_random_rational


class FormalGroup(Formal):

    def __init__(self, name=None, id=None):
        super().__init__(name=name, id=id)

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        return MM(self.name())


class FormalRing(Formal):

    def __init__(self, name=None, id=None):
        super().__init__(name=name, id=id)

    def __getitem__(self, item):
        if isinstance(item, FormalGroup):
            return FormalGroupRing(self, item)
        else:
            pass  # TODO

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        return MM(self.name())


class FormalGroupRing(FormalRing):

    def __init__(self, ring, group, name=None, id=None):
        super().__init__(name=name, id=id)
        self.ring = ring
        self.group = group


class FormalField(FormalRing):

    pass


class FormalNumberField(FormalField):

    def build_galois_group_underlying_set(self, base_field):
        raise NotImplementedError()


class TheRationalNumbers(FormalNumberField):

    def __init__(self):
        super().__init__(r'\mathbb{Q}', "QQ")

    def __call__(self, *args):
        if len(args) == 1 and isinstance(args[0], FormalPrimitiveRootOfUnity):
            zeta = args[0]
            return FormalCyclotomicField(gen=zeta)
        else:
            raise NotImplementedError()

# The Rational Numbers, as a fixed instance:
QQ = TheRationalNumbers()


class FormalGaloisGroup(FormalGroup):

    def __init__(self, ext_field, base_field=QQ, name=None, id=None):
        super().__init__(name=name, id=id)
        self.ext_field = ext_field
        self.base_field = base_field

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        options:

            form: FormOpt
                Default: name
                name: self.name()
                value: ask self.ext_field to produce a representation of the
                    underlying set
                symbolic: Gal(E/F) with E = self.ext_field, F = self.base_field
                verbal: "the Galois group of .... over ..."

        subpaths:

            'ext': self.ext_field
            'base': self.base_field
            'uset': only for {'form': 'value'} case: the underlying set
        """
        form = mode.get('form', FormOpt.NAME)

        if form == FormOpt.NAME:
            return MM(self.name())
        elif form == FormOpt.VALUE:
            assert isinstance(self.ext_field, FormalNumberField)
            fwdMode = self.getFwdMode(self, 'uset', rules, path)
            uset = self.ext_field.build_galois_group_underlying_set(self.base_field, mode=fwdMode)
            return self.fwd(uset, 'uset', rules, path)

        ext = self.fwd(self.ext_field, 'ext', rules, path)
        base = self.fwd(self.base_field, 'base', rules, path)

        if form == FormOpt.SYMBOLIC:
            return MM(r'\Gal(') + ext + MM('/') + base + MM(')')
        elif form == FormOpt.VERBAL:
            return 'the Galois group of ' + ext + ' over ' + base


class FormalPrimitiveRootOfUnity(Formal):

    def __init__(self, m=None, name=r'\zeta', id=None):
        super().__init__(name=name, id=id)
        self.m = wrap(m) if m is not None else None

    def order(self):
        return self.m

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        mode options:

            form: FormOpt
                name: self.name()
                value: write as a complex exponential
                symbolic: put self.m as subscript on self.name()
                verbal: describe verbally

                Default: 'name'

        subpaths:

            'order': self.m
        """
        form = mode.get('form', FormOpt.NAME)

        if form == FormOpt.NAME:
            return MM(self.name())

        if form == FormOpt.VERBAL:
            if self.m is None:
                return 'a primitive root of unity'
            else:
                m_ordinal = self.fwd(self.m, 'order', rules, path, modifier={'ordinal': True})
            return 'a primitive ' + m_ordinal + ' root of unity'

        assert self.m is not None

        order = self.fwd(self.m, 'order', rules, path)

        if form == FormOpt.SYMBOLIC:
            base = MM(self.name())
            return base + MM('_{') + order + MM('}')
        else:
            assert form == FormOpt.VALUE
            return MM(r'\mathrm{e}^{2\pi i/%s}' % order)


class FormalCyclotomicField(FormalNumberField):

    def __init__(self, m=None, gen=None, name=None, id=None):
        FormalNumberField.__init__(self, name=name, id=id)
        self.basefield = QQ
        if m is not None:
            # In this case we ignore gen.
            self.m = wrap(m)
            self.gen = FormalPrimitiveRootOfUnity(m)
        elif gen is not None:
            assert isinstance(gen, FormalPrimitiveRootOfUnity)
            self.m = wrap(gen.order())
            self.gen = gen
        else:
            # Both m and gen are None.
            self.m = m
            self.gen = gen

    def is_prime(self):
        return self.m.prime if self.m is not None else False

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        mode options:

            form: FormOpt
                Default: 'name'

        subpaths:
            'gen': self.gen
            'order': self.m
            'basefield': self.basefield
        """
        form = mode.get('form', FormOpt.NAME)

        if form == FormOpt.NAME:
            return MM(self.name())

        # TODO:
        #  By analogy to what we're now doing with the GaloisGroup class,
        #  maybe 'value' should mean we return our representation of our
        #  underlying set (while 'symbolic' still means what it means here).
        #  In general, I suppose, 'value' for any algebraic structure could
        #  mean a representation of the underlying set.

        elif form in FormOpt.valsym:
            basefield = self.fwd(self.basefield, 'basefield', rules, path)
            gen = self.fwd(self.gen, 'gen', rules, path)
            return basefield + MM("(") + gen + MM(")")

        elif form == FormOpt.VERBAL:
            if self.m is None:
                return 'a cyclotomic field'
            m_ordinal = self.fwd(self.m, 'order', rules, path, modifier={'ordinal': True})
            return 'the ' + m_ordinal + ' cyclotomic field'

    def build_formal_element(
            self,
            coeff_form = None,
            coeff_index = None,
            random_coeffs = False,
            coeff_base = 'a',
            elide_after = 3,
            falling_powers = False
    ):
        """
        Build and return a formal object to represent an element of this structure.

        coeff_form, random_coeffs, coeff_base, coeff_index:
            These options have to do with setting the kind of coefficients you want.

            coeff_form: You can set whatever coefficient form you want, using coeff_form.

            coeff_index: If you pass a coeff_form then, unless it is a constant, it should
                have at least one FormalVariable occurring somewhere within it, to serve as
                the iteration index. You must pass the desired FormalVariable for coeff_index,
                so that we can substitute values for it, as we build a formal sum.

            random_coeffs: If coeff_form is None and random_coeffs is True, we will
                generate "nice random" coeffs.

            coeff_base: If coeff_form is None and random_coeffs is False, then we will
                write the coeffs as a sequence of subscripted variables, and you can choose
                the base letter in coeff_base.

        elide_after, falling_powers:
            These options control what kind of terms you get, and in what order.

            elide_after: Pass a positive integer if you want an elision (...) after that
                many initial terms. Set to 0 if you do not want an elision (i.e. you want
                to spell out all the terms).

            falling_powers: Set True if you want the terms to go from high powers of the
                generator to low, reading left to right. Otherwise they go from low to high.
        """

        if self.is_prime():

            i = FormalVariable('i') if coeff_index is None else coeff_index
            if coeff_form is None:
                if random_coeffs:
                    a = lambda k: formalQuoFromFrac(nice_random_rational())
                    coeff_form = FormalLookup(i, a)
                else:
                    a = FormalString(coeff_base)
                    coeff_form = a._(i)

            term_form = coeff_form * self.gen ** i

            mval = self.m.value()
            if mval is not None:
                # When m does have a numerical value, the number of terms before
                # elision is capped at m - 4.
                elide_after = min(elide_after, mval - 4)
            else:
                # When m does not have a numerical value, then elision is required.
                if elide_after < 1:
                    elide_after = 3

            if elide_after > 0:
                m = self.m
                if falling_powers:
                    rng = [m - (k+2) for k in range(elide_after)] + [..., 0]
                else:
                    rng = list(range(elide_after)) + [..., m - 2]
            else:
                rng = range(mval - 1)
                if falling_powers:
                    rng = reversed(rng)

            return FormalRangeSum(rng, term_form, i)

        else:
            # m is not known to be prime
            ...  # TODO
            raise NotImplementedError()


    def build_formal_set(self, **kwargs):
        """
        Build and return a formal object to represent the underlying set of
        this structure.

        kwargs: accepts the same keyword args as the `build_formal_element` method.
        """
        kwargs.update({
            'random_coeffs': False
        })
        alpha = self.build_formal_element(**kwargs)
        coeff = alpha.generic_term().factors()[0]
        cond = coeff |in_| QQ
        return FormalSet(alpha, condition=cond)

    def build_galois_group_underlying_set(self, base_field, mode=None):
        mode = mode or {}
        if self.is_prime():

            sig = FormalString(r'\sigma')

            generator = mode.get('generator')

            if generator is None:
                r = FormalVariable('r')
                elt = FormalMapping(sig._(r), self, self, [self.gen], self.gen ** r)
                uset = FormalRangeSet([1, 2, ..., self.m - 1], elt, r)

            else:
                from stylgebra.elnt import FormalIntResidue
                m = self.m.value()
                if generator == 'auto':
                    generator = primitive_root(m)
                gamma = FormalIntResidue(generator, m, name=r'\gamma', id='gamma')
                k = FormalVariable('k')
                elt = FormalMapping(sig._(k), self, self, [self.gen], self.gen ** (gamma ** k))
                uset = FormalRangeSet([1, 2, ..., self.m - 1], elt, k)

            return uset

        else:
            # m is not known to be prime
            ...  # TODO
            raise NotImplementedError()

##############################################################################

def try_00():
    p = FormalInteger(13, 'p')
    K = FormalCyclotomicField(p, name="K")
    s = K.format({
        'form': 'symbolic'
    })
    print(s)

if __name__ == "__main__":
    try_00()
