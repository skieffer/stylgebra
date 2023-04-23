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

from stylgebra.algebra import *
from tests.conftest import check


exp_algebra_00 = [
    r"\zeta",
    r"\mathrm{e}^{2\pi i/7}",
    r"a primitive $7^{\mathrm{th}}$ root of unity",
    r"\xi",
    r"a primitive root of unity",
    r"$\xi$, a primitive root of unity",
]
def test_algebra_00():
    zeta = FormalPrimitiveRootOfUnity(7)
    check(zeta.format(), exp_algebra_00[0])
    check(zeta.format(rules={
        "@": {
            'form': 'value'
        }
    }), exp_algebra_00[1])
    check(zeta.format(rules={
        "@": {
            'form': 'verbal'
        }
    }), exp_algebra_00[2])

    xi = FormalPrimitiveRootOfUnity(name=r'\xi')
    s = xi.format()
    t = xi.format(rules={
        "@": {
            'form': 'verbal'
        }
    })
    check(s, exp_algebra_00[3])
    check(t, exp_algebra_00[4])
    check(s + ', ' + t, exp_algebra_00[5])


exp_algebra_01 = [
    "K",
    r"\mathbb{Q}(\zeta)",
    r"\mathbb{Q}(\zeta_{p})",
    r"\mathbb{Q}(\zeta_{13})",
    r"\mathbb{Q}(\mathrm{e}^{2\pi i/p})",
    r"\mathbb{Q}(\mathrm{e}^{2\pi i/13})",
    r"the $p^{\mathrm{th}}$ cyclotomic field",
    r"the $13^{\mathrm{th}}$ cyclotomic field",
]
def test_algebra_01():
    p = FormalInteger(13, 'p')
    K = FormalCyclotomicField(p, name="K")

    check(K.format(), exp_algebra_01[0])

    check(K.format({
        'form': 'symbolic'
    }), exp_algebra_01[1])

    # Instead of defining a separate mode, we can put the top-level mode
    # into the rules dict, under the key "@". This matches only items whose
    # path is empty, and that will be only the top-level item.
    check(K.format(rules={
        "@": {
            'form': 'symbolic'
        },
        '@gen': {
            'form': 'symbolic'
        }
    }), exp_algebra_01[2])

    check(K.format(rules={
        "@": {
            'form': 'symbolic'
        },
        '@gen': {
            'form': 'symbolic'
        },
        "@gen-order": {
            'form': 'value'
        }
    }), exp_algebra_01[3])

    check(K.format(rules={
        "@": {
            'form': 'symbolic'
        },
        "@gen": {
            'form': 'value'
        }
    }), exp_algebra_01[4])

    check(K.format(rules={
        "@": {
            'form': 'symbolic'
        },
        "@gen": {
            'form': 'value'
        },
        "@gen-order": {
            'form': 'value'
        }
    }), exp_algebra_01[5])

    check(K.format({
        'form': 'verbal'
    }), exp_algebra_01[6])

    check(K.format(rules={
        "@": {
            'form': 'verbal'
        },
        "@order": {
            'form': 'value'
        }
    }), exp_algebra_01[7])


exp_algebra_02 = [
    r"a_{0} + a_{1} \zeta + a_{2} \zeta^{2} + \cdots + a_{p - 2} \zeta^{p - 2}",
    r"a_{0} + a_{1} \zeta + \cdots + a_{p - 2} \zeta^{p - 2}",
    r"a_{p - 2} \zeta^{p - 2} + a_{p - 3} \zeta^{p - 3} + \cdots + a_{0}",
    r"a_{0} + a_{1} \zeta + a_{2} \zeta^{2} + a_{3} \zeta^{3} + a_{4} \zeta^{4} + a_{5} \zeta^{5}",
    r"c_{0} + c_{1} \zeta + c_{2} \zeta^{2} + \cdots + c_{p - 2} \zeta^{p - 2}",
    r"c_{0} + c_{1} \zeta + c_{2} \zeta^{2} + \cdots + c_{7 - 2} \zeta^{7 - 2}",
    r"c_{0} + c_{1} \zeta + c_{2} \zeta^{2} + \cdots + c_{5} \zeta^{5}",
    r"2 + 3 \zeta + 5 \zeta^{2} + \cdots + 13 \zeta^{p - 2}",
]
def test_algebra_02():
    p = FormalInteger(7, 'p')
    K = FormalCyclotomicField(p, name="K")

    elt = K.build_formal_element()
    check(elt.format(), exp_algebra_02[0])

    elt = K.build_formal_element(elide_after=2)
    check(elt.format(), exp_algebra_02[1])

    elt = K.build_formal_element(elide_after=2, falling_powers=True)
    check(elt.format(), exp_algebra_02[2])

    elt = K.build_formal_element(elide_after=0)
    check(elt.format(), exp_algebra_02[3])

    elt = K.build_formal_element(coeff_base='c')
    check(elt.format(), exp_algebra_02[4])
    check(elt.format(rules={
        "#p": {
            'form': 'value'
        }
    }), exp_algebra_02[5])

    # The hard way:
    check(elt.format(rules={
        "@term4-factor0-sub-subst": {
            'form': 'value'
        },
        "@term4-factor1-power-subst": {
            'form': 'value'
        }
    }), exp_algebra_02[6])

    # The easy way:
    check(elt.format(rules={
        "@term4 Sum": {
            'form': 'value'
        }
    }), exp_algebra_02[6])

    # Or just address all variables; needn't confine to term4:
    check(elt.format(rules={
        "Variable @subst": {
            'form': 'value'
        }
    }), exp_algebra_02[6])

    # Or you can address the iteration variable, either by knowing that
    # by default it will be 'i', or by setting your own index:
    elt = K.build_formal_element(coeff_index=FormalVariable('j'), coeff_base='c')
    check(elt.format(rules={
        "#j @subst": {
            'form': 'value'
        }
    }), exp_algebra_02[6])

    i = FormalVariable('i')
    f = FormalLookup(i, [2, 3, 5, ..., ..., 13])
    elt = K.build_formal_element(coeff_form=f, coeff_index=i)
    check(elt.format(), exp_algebra_02[7])

    elt = K.build_formal_element(random_coeffs=True)
    print(elt.format())


exp_algebra_03 = [
    r'\left\{ a_{0} + a_{1} \zeta + a_{2} \zeta^{2} + \cdots + a_{p - 2} \zeta^{p - 2} : a_{i} \in \mathbb{Q} \right\}',
    r"\left\{ a_{0} + a_{1} \zeta + a_{2} \zeta^{2} + \cdots + a_{p - 2} \zeta^{p - 2} : \mbox{$a_{i}$ is an element of $\mathbb{Q}$} \right\}",
    r"$\left\{ a_{0} + a_{1} \zeta + a_{2} \zeta^{2} + \cdots + a_{p - 2} \zeta^{p - 2} \right\}$ where $a_{i}$ is an element of $\mathbb{Q}$",
]
def test_algebra_03():
    p = FormalInteger(7, 'p')
    K = FormalCyclotomicField(p, name="K")
    S = K.build_formal_set()

    check(S.format({
        'form': 'symbolic'
    }), exp_algebra_03[0])

    check(S.format({
        'form': 'symbolic'
    }, {
        '@cond': {
            'form': 'verbal'
        }
    }), exp_algebra_03[1])

    check(S.format({
        'form': 'symbolic',
        'cond': 'where',
    }, {
        '@cond': {
            'form': 'verbal',
        }
    }), exp_algebra_03[2])


def test_algebra_04():
    p = FormalInteger(7, 'p')
    K = FormalCyclotomicField(p, name="K")
    G = FormalGaloisGroup(K, name="G")

    check(G.format(), "G")

    check(G.format(rules={
        "@": {
            'form': 'symbolic'
        }
    }), r'\Gal(K/\mathbb{Q})')
    check(G.format(rules={
        "@": {
            'form': 'symbolic'
        },
        "@ext": {
            'form': 'symbolic'
        }
    }), r'\Gal(\mathbb{Q}(\zeta)/\mathbb{Q})')
    check(G.format(rules={
        "@": {
            'form': 'symbolic'
        },
        "@ext": {
            'form': 'symbolic'
        },
        "@ext-gen": {
            'form': 'value'
        }
    }), r'\Gal(\mathbb{Q}(\mathrm{e}^{2\pi i/p})/\mathbb{Q})')

    check(G.format(rules={
        "@": {
            'form': 'verbal'
        }
    }), r'the Galois group of $K$ over $\mathbb{Q}$')
    check(G.format(rules={
        "@": {
            'form': 'verbal'
        },
        "@ext": {
            'form': 'symbolic'
        }
    }), r'the Galois group of $\mathbb{Q}(\zeta)$ over $\mathbb{Q}$')

    check(G.format(rules={
        "@": {
            'form': 'value'
        },
        "@uset": {
            'form': 'symbolic'
        }
    }), r'\left\{ \sigma_{1}, \sigma_{2}, \ldots, \sigma_{p - 1} \right\}')

    check(G.format(rules={
        "@": {
            'form': 'value'
        },
        "@uset": {
            'form': 'symbolic',
            'range': 'bind',
        }
    }), r'\left\{ \sigma_{r} : 1 \leq r \leq p - 1 \right\}')

    check(G.format(rules={
        "@": {
            'form': 'value'
        },
        "@uset": {
            'form': 'symbolic',
            'range': 'bind',
            'cond': 'vbar',
        },
        "@uset-elt0": {
            'form': 'name-mapsto'
        }
    }), r'\left\{ \sigma_{r}: \zeta \mapsto \zeta^{r} \mid 1 \leq r \leq p - 1 \right\}')

    check(G.format(rules={
        "@": {
            'form': 'value'
        },
        "@uset": {
            'form': 'symbolic'
        },
        "@uset-elt[i]": {
            'form': 'mapsto'
        }
    }), r'\left\{ \zeta \mapsto \zeta, \zeta \mapsto \zeta^{2}, \ldots, \zeta \mapsto \zeta^{p - 1} \right\}')

    check(G.format(rules={
        "@": {
            'form': 'value'
        },
        "@uset": {
            'form': 'symbolic',
            'generator': 'auto',
            'range': 'bind',
        }
    }), r'\left\{ \sigma_{k} : 1 \leq k \leq p - 1 \right\}')

    check(G.format(rules={
        "@": {
            'form': 'value'
        },
        "@uset": {
            'form': 'symbolic',
            'generator': 'auto',
            'range': 'bind',
            'cond': 'vbar',
        },
        "@uset-elt0": {
            'form': 'name-mapsto'
        }
    }), r'\left\{ \sigma_{k}: \zeta \mapsto \zeta^{\gamma^{k}} \mid 1 \leq k \leq p - 1 \right\}')

    check(G.format(rules={
        "@": {
            'form': 'value'
        },
        "@uset": {
            'form': 'symbolic',
            'generator': 'auto',
        },
        "@uset-elt[i]": {
            'form': 'mapsto'
        }
    }), r'\left\{ \zeta \mapsto \zeta^{\gamma}, \zeta \mapsto \zeta^{\gamma^{2}}, \ldots, \zeta \mapsto \zeta^{\gamma^{p - 1}} \right\}')

    check(G.format(rules={
        "@": {
            'form': 'value'
        },
        "@uset": {
            'form': 'symbolic',
            'generator': 'auto',
        },
        "@uset-elt[i]": {
            'form': 'mapsto'
        },
        "#gamma": {
            'form': 'value'
        }
    }), r'\left\{ \zeta \mapsto \zeta^{3}, \zeta \mapsto \zeta^{3^{2}}, \ldots, \zeta \mapsto \zeta^{3^{p - 1}} \right\}')

    # Commenting out the last two tests for now.
    # The solution in keeping with our overall design would be to have a styling
    # option for instances of SymPy's `SymmetricModularInteger____` classes
    # (i.e. elements of finite fields), where you can say whether you want the
    # form `r mod m` or simply `r`.
    r"""
    check(G.format(rules={
        "@": {
            'form': 'value'
        },
        "@uset": {
            'form': 'symbolic',
            'generator': 'auto',
        },
        "@uset-elt[i]": {
            'form': 'mapsto'
        },
        "@uset-elt[i]-value-power": {
            'form': 'value'
        }
    }), r'\left\{ \zeta \mapsto \zeta^{3}, \zeta \mapsto \zeta^{2}, \ldots, \zeta \mapsto \zeta \right\}')
    
    check(G.format(rules={
        "@": {
            'form': 'value'
        },
        "@uset": {
            'form': 'symbolic',
            'generator': 5,
        },
        "@uset-elt[i]": {
            'form': 'mapsto'
        },
        "@uset-elt[i]-value-power": {
            'form': 'value'
        }
    }), r'\left\{ \zeta \mapsto \zeta^{5}, \zeta \mapsto \zeta^{4}, \ldots, \zeta \mapsto \zeta \right\}')
    """
