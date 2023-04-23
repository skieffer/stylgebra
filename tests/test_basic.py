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

from stylgebra.expressions import *
from stylgebra.relations import *

from tests.conftest import check


def test_basic_01():
    a = FormalString('a')
    ivar = FormalVariable('i')
    ai = a._(ivar)
    check(
        [ai.format(rules={'#i': i}) for i in range(0, 5)],
        "['a_{0}', 'a_{1}', 'a_{2}', 'a_{3}', 'a_{4}']"
    )


def test_basic_02():
    p = FormalInteger(11, 'p')
    check(p.format({'form': 'name'}), 'p')
    check(p.format({'form': 'value'}), '11')
    check(p.format({'form': 'verbal'}), 'an odd, positive prime')
    check('the ' + p.format({
        'form': 'name',
        'ordinal': True
    }), r'the $p^{\mathrm{th}}$')
    check('the ' + p.format({
        'form': 'value',
        'ordinal': True
    }), r'the $11^{\mathrm{th}}$')
    check('the ' + FormalInteger(21).format({
        'form': 'value',
        'ordinal': True
    }), r'the $21^{\mathrm{st}}$')
    check('the ' + FormalInteger(1).format({
        'form': 'value',
        'ordinal': True
    }), r'the $1^{\mathrm{st}}$')
    check('the ' + FormalInteger(2).format({
        'form': 'value',
        'ordinal': True
    }), r'the $2^{\mathrm{nd}}$')
    check('the ' + FormalInteger(3).format({
        'form': 'value',
        'ordinal': True
    }), r'the $3^{\mathrm{rd}}$')


exp_basic_03 = [
    r"\zeta^{r}",
    r"\zeta^{-1}",
    r"\frac{1}{\zeta}",
]
def test_basic_03():
    zeta = FormalVariable(r'\zeta')
    r = FormalInteger(-1, 'r')
    ztor = zeta**r
    check(ztor.format({}, {'@power': {'form': 'name'}}), exp_basic_03[0])
    check(ztor.format({}, {'@power': {'form': 'value'}}), exp_basic_03[1])
    check(ztor.format({'negative': 'frac'}, {'@power': {'form': 'value'}}), exp_basic_03[2])


def test_basic_04():
    b = FormalInteger(2, 'b')
    r = FormalInteger(3, 'r')
    btor = b**r
    check(btor.format(), 'b^{r}')
    check(btor.format({}, {
        '@base': {'form': 'value'},
        '@power': {'form': 'value'}
    }), '2^{3}')
    check(btor.format({'form': 'value'}), '8')


exp_basic_05 = [
    r"\sigma_{i}",
    r"\sigma_{i}(\zeta)",
    r"\zeta^{i}",
    r"\sigma_{i}: F \rightarrow F",
    r"\sigma_{i}: \zeta \mapsto \zeta^{i}",
    r"\sigma_{5}: \zeta \mapsto \zeta^{5}",
    r"\sigma_{i}: \xi \mapsto \zeta^{i}",
    r"\sigma_{i}: \xi \mapsto \xi^{i}",
]
def test_basic_05():
    sig = FormalString(r'\sigma')
    i = FormalVariable('i')

    #p = FormalInteger(11, 'p')
    #F = CyclotomicField(p)
    F = FormalVariable("F")

    zeta = FormalVariable(r'\zeta', 'zeta')
    sigi = FormalMapping(sig._(i), F, F, [zeta], zeta ** i)

    check(sigi.format(), exp_basic_05[0])
    check(sigi.format({
        'form': 'name-args'
    }), exp_basic_05[1])
    check(sigi.format({
        'form': 'value'
    }), exp_basic_05[2])
    check(sigi.format({
        'form': 'map'
    }), exp_basic_05[3])
    check(sigi.format({
        'form': 'name-mapsto'
    }), exp_basic_05[4])
    check(sigi.format({'form': 'name-mapsto'}, {'#i': 5}), exp_basic_05[5])

    check(sigi.format({'form': 'name-mapsto'}, {
        '@arg0': FormalVariable(r'\xi').format()
    }), exp_basic_05[6])

    check(sigi.format({'form': 'name-mapsto'}, {'#zeta': r'\xi'}), exp_basic_05[7])


exp_basic_06 = [
    r"\left(a + b\right) + c",
    r"a + b + c",
    r"3",
    r"3",
    r"\left(1 + 2\right) + 0",
    r"\left(a + b\right) - \left(c + d\right)",
    r"a + b - c - d",
    r"-c + a + b - d",
    r"\left(-c + a\right) + \left(b - d\right)",
    r"-1",
    r"-1",
    r"\left(a + b\right) - d",
    r"\left(a + b\right) - \left(0 + d\right)",
    r"a + b - 0 - d",
    r"-a + b",
    r"a - b",
    r"a + b + \cdots + d",
]
def test_basic_06():
    a = FormalInteger(1, 'a')
    b = FormalInteger(2, 'b')
    c = FormalInteger(0, 'c')
    d = FormalInteger(4, 'd')
    el = FormalEllipsis()

    s0 = a + b + c
    check(s0.format(), exp_basic_06[0])
    check(s0.flattened().format(), exp_basic_06[1])
    check(s0.format({'form': 'value'}), exp_basic_06[2])
    check(s0.flattened().format({'form': 'value'}), exp_basic_06[3])
    check(s0.format({
        'show-zeros': True
    }, {
        '#a': {'form': 'value'},
        '#b': {'form': 'value'},
        '#c': {'form': 'value'},
    }), exp_basic_06[4])

    s1 = (a + b) - (c + d)
    check(s1.format(), exp_basic_06[5])
    check(s1.flattened().format(), exp_basic_06[6])
    check(s1.flattened().permuted([2, 0, 1, 3]).format(), exp_basic_06[7])
    check(s1.flattened().split([
        [2, 0], [1, 3]
    ]).format(), exp_basic_06[8])
    check(s1.format({'form': 'value'}), exp_basic_06[9])
    check(s1.flattened().format({'form': 'value'}), exp_basic_06[10])
    check(s1.format(rules={'#c': {'form': 'value'}}), exp_basic_06[11])

    check(s1.format({}, {
        '#c': {'form': 'value'},
        '@term1': {
            'show-zeros': True
        },
    }), exp_basic_06[12])

    s2 = s1.flattened()
    check(s2.format({
        'show-zeros': True
    }, {
        '#c': {'form': 'value'},
    }), exp_basic_06[13])

    s3 = -a + b
    check(s3.format(), exp_basic_06[14])

    s4 = a + (-b)
    check(s4.format(), exp_basic_06[15])

    s5 = a + b + el + d
    s5.flatten()
    check(s5.format(), exp_basic_06[16])


exp_basic_07 = [
    r"a_{0} + a_{1} + a_{2} + a_{3} + a_{4}",
    r"a_{0} + a_{1} + a_{2} + \cdots + a_{4}",
]
def test_basic_07():
    a = FormalString('a')
    i = FormalVariable('i')
    ai = a._(i)
    #s = ai + ai + ai + ai + ai
    s0 = sum([ai]*5, FormalSum())
    s0.flatten()

    s1 = ai + ai + ai + ooo + ai
    s1.flatten()

    # print(s.format(rules={'i':7}))

    check(s0.format(rules={
        r'@term[i] #i': lambda i: i
    }), exp_basic_07[0])

    check(s1.format(rules={
        r'@term[i] #i': lambda i: i
    }), exp_basic_07[1])


exp_basic_08 = [
    r"a_{0} + a_{1} + \cdots + a_{p - 2}",
    r"a_{0} + a_{1} + \cdots + a_{1}",
    r"a_{0} + a_{1} + \cdots + a_{13 - 2}",
    r"a_{0} + a_{1} + \cdots + a_{11}",
    r"f: p \mapsto a_{0} + a_{1} + \cdots + a_{p - 2}",
    r"\sum_{i = 0}^{p - 2} a_{i}",
]
def test_basic_08():
    a = FormalString('a')
    i = FormalVariable('i')
    p = FormalInteger(13, 'p')
    s = FormalRangeSum([0, 1, ..., p - 2], a._(i), i)

    f = FormalMapping(FormalString('f'), None, None, [p], s)

    check(s.format(), exp_basic_08[0])

    check(s.format({}, {
        '@term3-sub': 1
    }), exp_basic_08[1])

    check(s.format({}, {
        '#p': {'form': 'value'}
    }), exp_basic_08[2])

    check(s.format({}, {
        '@term3-sub-subst': {'form': 'value'}
    }), exp_basic_08[3])

    check(f.format({
        'form': 'name-mapsto'
    }), exp_basic_08[4])

    check(s.format({
        'range': 'bind'
    }), exp_basic_08[5])


exp_basic_09 = [
    r"['2', '3', '5', '7']",
    r"['0', '1', '2', '3', '1', '2', '3', '4', '2', '3', '4', '5', '3', '4', '5', '6']",
    r"['1', '2', '3', '4', '1', '4', '9', '16', '1', '8', '27', '64', '1', '16', '81', '256']",
]
def test_basic_09():
    i = FormalVariable('i')
    j = FormalVariable('j')

    ai = FormalLookup([i], [2, 3, 5, 7])
    V = []
    for ival in range(4):
        V.append(ai.format(rules={
            '#i': ival
        }))
    check(V, exp_basic_09[0])

    sij = FormalLookup([i, j], lambda i, j: i + j)
    V = []
    for ival in range(4):
        for jval in range(4):
            V.append(sij.format(rules={
                '#i': ival,
                '#j': jval,
            }))
    check(V, exp_basic_09[1])

    tij = FormalLookup([i, j], [
        [1, 2, 3, 4],
        [1, 4, 9, 16],
        [1, 8, 27, 64],
        [1, 16, 81, 256],
    ])
    V = []
    for ival in range(4):
        for jval in range(4):
            V.append(tij.format(rules={
                '#i': ival,
                '#j': jval,
            }))
    check(V, exp_basic_09[2])


exp_basic_10 = [
    r"1",
    r"a^{0}",
    r"a",
    r"a^{1}",
    r"a^{2}",
    r"a^{2}",
]
def test_basic_10():
    a = FormalString('a')
    check((a ** 0).format(), exp_basic_10[0])
    check((a.sup(0)).format(), exp_basic_10[1])
    check((a ** 1).format(), exp_basic_10[2])
    check((a.sup(1)).format(), exp_basic_10[3])
    check((a ** 2).format(), exp_basic_10[4])
    check((a.sup(2)).format(), exp_basic_10[5])


exp_basic_11 = [
    r"\left(\left(a b\right) c\right) d",
    r"a b c d",
    r"c a d b",
    r"-b d",
    r"0",
    r"\left(a d\right) \left(c b\right)",
    r"210",
    r"0",
    r"-2 \cdot 0",
    r"-1 \cdot 2 \cdot 1 \cdot 0",
    r"(-1)(-2)(-1)(0)",
]
def test_basic_11():
    a = FormalVariable('a')
    b = FormalVariable('b')
    c = FormalVariable('c')
    d = FormalVariable('d')

    pr0 = a * b * c * d
    pr1 = pr0.flattened()

    check(pr0.format(), exp_basic_11[0])

    check(pr1.format(), exp_basic_11[1])
    check(pr1.permuted([2, 0, 3, 1]).format(), exp_basic_11[2])
    check(pr1.format(rules={
        '#a': 1,
        '#c': -1
    }), exp_basic_11[3])
    check(pr1.format(rules={
        '#d': 0
    }), exp_basic_11[4])

    pr2 = pr1.split([
        [0, 3], [2, 1]
    ])
    check(pr2.format(), exp_basic_11[5])

    print()

    check(pr1.format({
        'form': 'value'
    }, {
        '#a': 2, '#b': 3, '#c': 5, '#d': 7
    }), exp_basic_11[6])

    check(pr1.format({
        'mult-symb': 'dot',
    }, {
        '#a': -1, '#b': -2, '#c': -1, '#d': 0
    }), exp_basic_11[7])

    check(pr1.format({
        'mult-symb': 'dot',
        'collapse-zero': False
    }, {
        '#a': -1, '#b': -2, '#c': -1, '#d': 0
    }), exp_basic_11[8])

    check(pr1.format({
        'mult-symb': 'dot',
        'collapse-zero': False,
        'show-unity': True
    }, {
        '#a': -1, '#b': -2, '#c': -1, '#d': 0
    }), exp_basic_11[9])

    check(pr1.format({
        'mult-symb': 'paren',
        'collapse-zero': False,
        'show-unity': True,
        'signs': 'auto'
    }, {
        '#a': -1, '#b': -2, '#c': -1, '#d': 0
    }), exp_basic_11[10])


exp_basic_12 = [
    r"a_{0} + a_{1} \zeta + \cdots + a_{p - 2} \zeta^{p - 2}",
    r"$\left\{ a_{0} + a_{1} \zeta + \cdots + a_{p - 2} \zeta^{p - 2} \right\}$ where $a_i \in \mathbb{Q}$",
    r"the set of all $a_{0} + a_{1} \zeta + \cdots + a_{p - 2} \zeta^{p - 2}$ such that $a_i \in \mathbb{Q}$"
]
def test_basic_12():
    a = FormalString('a')
    i = FormalVariable('i')
    zeta = FormalVariable(r'\zeta', 'zeta')
    p = FormalInteger(11, 'p')

    alpha = FormalRangeSum([0, 1, ..., p-2], a._(i)*zeta**i, i)
    check(alpha.format(), exp_basic_12[0])

    K = FormalSet(alpha, condition=FormalString(r'a_i \in \mathbb{Q}'), name="K")
    check(K.format({
        'form': 'symbolic',
        'cond': 'where',
    }), exp_basic_12[1])

    check(K.format({
        'form': 'verbal'
    }), exp_basic_12[2])


exp_basic_13 = [
    r"\frac{1 - \zeta^{g}}{2}",
    r"\frac{1}{1 - \zeta^{g}}",
    r"\frac{\left(1 - \zeta^{g}\right)}{\left(1 - \zeta\right)}",
    r"\frac{\left(1 - \zeta^{6}\right)}{\left(1 - \zeta\right)}",
    r"\frac{\left(1 - \zeta^{3 \cdot 5}\right)}{\left(1 - \zeta\right)}",
    r"\frac{\left(1 - \zeta^{3 \cdot 5}\right)}{\left(1 - \zeta\right)}",
    r"\frac{\left(1 - \zeta^{3 \cdot 5}\right)}{\left(1 - \zeta\right)}",
]
def test_basic_13():
    zeta = FormalVariable(r'\zeta', 'zeta')
    g = FormalVariable('g')

    quo = (1 - zeta**g) / (1 - zeta)
    quo0 = (1 - zeta ** g) / 2
    quo1 = 1 / (1 - zeta ** g)

    check(quo0.format(), exp_basic_13[0])
    check(quo1.format(), exp_basic_13[1])

    check(quo.format({
        'brackets-top': 'round',
        'brackets-bot': 'round'
    }), exp_basic_13[2])

    check(quo.format({
        'brackets-top': 'round',
        'brackets-bot': 'round'
    }, {
        '#g': 6
    }), exp_basic_13[3])

    check(quo.format({
        'brackets-top': 'round',
        'brackets-bot': 'round'
    }, {
        '#g': FormalProduct([3, 5]),
        # We can set the mode for the thing we're substituting for `g`
        # by using its address in the syntax tree:
        '@top-term1-power-subst': {
            'mult-symb': 'dot'
        }
    }), exp_basic_13[4])

    check(quo.format({
        'brackets-top': 'round',
        'brackets-bot': 'round'
    }, {
        '#g': FormalProduct([3, 5]),
        # But it is easier to find it this way:
        '#g @subst': {
            'mult-symb': 'dot'
        }
    }), exp_basic_13[5])

    check(quo.format({
        'brackets-top': 'round',
        'brackets-bot': 'round'
    }, {
        # Another way to do it is to format the thing _before_ substituting it;
        # i.e. to just substitute a string.
        '#g': FormalProduct([3, 5]).format({
            'mult-symb': 'dot'
        })
    }), exp_basic_13[6])


def test_basic_14():
    q = FormalQuotient(3, 7)
    check(q.format({'form': 'value'}), "3/7")

    a = FormalInteger(0)
    b = FormalInteger(1)
    c = FormalInteger(2)
    d = FormalInteger(3)

    q0 = a / d
    check(q0.format(), '0')

    q1 = c / b
    check(q1.format(), '2')

    q2 = (-b) / d
    check(q2.format(), r'-\frac{1}{3}')

    q3 = d / (-b)
    check(q3.format(), '-3')

    q4 = (-c) / (-d)
    check(q4.format(), r'\frac{2}{3}')


exp_basic_15 = [
    r"\left\{ 0, 1, 2, \ldots, q - 1 \right\}",
    r"the set $\left\{ 0, 1, 2, \ldots, q - 1 \right\}$",
]
def test_basic_15():
    q = FormalInteger(11, 'q')
    S = FormalSet([0, 1, 2, ooo, q - 1], name='S')
    t = S.format({
        'form': 'symbolic'
    })
    check(t, exp_basic_15[0])
    check('the set ' + t, exp_basic_15[1])

    E = FormalSet([])
    check(E.format({
        'form': 'verbal'
    }), 'the empty set')
    check(E.format({
        'form': 'symbolic'
    }), r'\varnothing')


def test_basic_16():
    x = FormalVariable('x')
    y = FormalVariable('y')
    f = FormalMapping('f', args=[x, y], value_form=x**2 + y**2)
    s = f.format({
        'form': 'name-args'
    })
    check(s, 'f(x, y)')
    check('the function ' + s, 'the function $f(x, y)$')
    check(f.format({
        'form': 'name-mapsto'
    }), r'f: x, y \mapsto x^{2} + y^{2}')


def test_basic_17():
    x = FormalVariable('x')
    y = FormalVariable('y')
    a = FormalInteger(2)
    b = FormalInteger(-3)
    c = FormalInteger(-5)

    p0 = x * a * y * b * c
    p0.flatten()
    check(p0.format(), r'2 \cdot 3 \cdot 5 x y')

    p1 = x * a * b * y
    p1.flatten()
    check(p1.format(), r'-2 \cdot 3 x y')

    check(p1.format({
        'signs': 'auto'
    }), r'2 \cdot -3 x y')

    check(p1.format({
        'numerals': 'dot'
    }), r'-x \cdot 2 \cdot 3 y')

    check(p1.format({
        'numerals': 'none'
    }), '-x 2 3 y')


def test_basic_18():
    x = FormalVariable('x')
    a = FormalInteger(2, 'a')
    check(x.format(a), 'a')
    check(x.format(a, {
        '#x @subst': {
            'form': 'value'
        }
    }), '2')
    check(x.format({
        'subst': a,
        'form': 'value'
    }), '2')


def test_basic_19():
    a = FormalString('a')
    i = FormalVariable('i')
    p = FormalInteger(13, 'p')

    su = FormalRangeSum([0, 1, ..., p - 2], a._(i), i)
    se = FormalRangeSet([0, 1, ..., p - 2], a._(i), i)
    check(su.format(), r'a_{0} + a_{1} + \cdots + a_{p - 2}')
    check(se.format(), r'\left\{ a_{0}, a_{1}, \ldots, a_{p - 2} \right\}')
    check(su.format({
        'range': 'bind'
    }), r'\sum_{i = 0}^{p - 2} a_{i}')
    check(se.format({
        'range': 'bind'
    }), r'\left\{ a_{i} : 0 \leq i \leq p - 2 \right\}')

    su = FormalRangeSum([0, 1, ..., p - 2, ...], a._(i), i)
    se = FormalRangeSet([0, 1, ..., p - 2, ...], a._(i), i)
    check(su.format(), r'a_{0} + a_{1} + \cdots + a_{p - 2} + \cdots')
    check(se.format(), r'\left\{ a_{0}, a_{1}, \ldots, a_{p - 2}, \ldots \right\}')
    check(su.format({
        'range': 'bind'
    }), r'\sum_{i = 0}^{\infty} a_{i}')
    check(se.format({
        'range': 'bind'
    }), r'\left\{ a_{i} : 0 \leq i < \infty \right\}')

    su = FormalRangeSum([..., -2, -1, 0, 1, 2, ...], a._(i), i)
    se = FormalRangeSet([..., -2, -1, 0, 1, 2, ...], a._(i), i)
    check(su.format(), r'\cdots + a_{-2} + a_{-1} + a_{0} + a_{1} + a_{2} + \cdots')
    check(se.format(), r'\left\{ \ldots, a_{-2}, a_{-1}, a_{0}, a_{1}, a_{2}, \ldots \right\}')
    check(su.format({
        'range': 'bind'
    }), r'\sum_{i = -\infty}^{\infty} a_{i}')
    check(se.format({
        'range': 'bind'
    }), r'\left\{ a_{i} : -\infty < i < \infty \right\}')

    su = FormalRangeSum([2, -3, 5, -7])
    se = FormalRangeSet([2, -3, 5, -7])
    check(su.format(), r'2 - 3 + 5 - 7')
    check(se.format(), r'\left\{ 2, -3, 5, -7 \right\}')

    S = FormalSet([], name="S")
    su = FormalRangeSum(None, a._(i), i, cond = i |in_| S)
    se = FormalRangeSet(None, a._(i), i, cond = i |in_| S)
    check(su.format({
        'range': 'bind'
    }, {
        "#S": {
            'form': 'name'
        }
    }), r'\sum_{i \in S} a_{i}')
    check(se.format({
        'range': 'bind'
    }, {
        "#S": {
            'form': 'name'
        }
    }), r'\left\{ a_{i} : i \in S \right\}')


def test_basic_20():
    p = FormalVariable('p')
    f = (1 - 1/p)**(-1)

    # When no range and no condition given, then just put the bound var itself as subscript.
    pr0 = FormalRangeProd([], gen_form=f, bound_var=p)
    check(pr0.format(), r'\prod_{p} \left(1 - \frac{1}{p}\right)^{-1}')

    # However, do not do the same in the case of a set. In other words, we do
    # NOT want to get r'\left\{ \left(1 - \frac{1}{p}\right)^{-1} : p \right\}.
    S0 = FormalRangeSet([], gen_form=f, bound_var=p)
    check(S0.format(), r'\left\{ \left(1 - \frac{1}{p}\right)^{-1} \right\}')

    check(pr0.format(rules={
        '@form': {
            'negative': 'frac'
        }
    }), r'\prod_{p} \frac{1}{1 - \frac{1}{p}}')

    S = [2, 3, 5, 7]
    pr1 = FormalRangeProd(S, gen_form=f, bound_var=p)
    check(pr1.format(), r'\left(1 - \frac{1}{2}\right)^{-1} \left(1 - \frac{1}{3}\right)^{-1} \left(1 - \frac{1}{5}\right)^{-1} \left(1 - \frac{1}{7}\right)^{-1}')

    # Here the |in_| coerces the python list S into a FormalSet automatically:
    pr2 = FormalRangeProd([], gen_form=f, bound_var=p, cond=p |in_| S)
    check(pr2.format(), r'\prod_{p \in \left\{ 2, 3, 5, 7 \right\}} \left(1 - \frac{1}{p}\right)^{-1}')
