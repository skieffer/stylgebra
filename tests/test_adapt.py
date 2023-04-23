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

from sympy import S, Add, symbols

from stylgebra.adapt import adapt_sympy_expr
from tests.conftest import check


def test_adapt_00():
    e = S.NegativeOne
    f = adapt_sympy_expr(e)
    s = f.format()
    check(s, "-1")


def test_adapt_01():
    x, y = symbols('x, y')
    a = Add(x, y, 3, evaluate=False)
    f = adapt_sympy_expr(a)
    s = f.format()
    check(s, "x + y + 3")


def test_adapt_02():
    x, y = symbols('x, y')
    a = Add(x, -y, evaluate=False)
    f = adapt_sympy_expr(a)
    s = f.format()
    check(s, "x - y")


def test_adapt_03():
    print()
    x = symbols('x')
    expr1 = x**(-1)
    expr2 = x**(-2)
    print('SymPy:')
    print(expr1)
    print(expr2)
    print('=============')

    formal1 = adapt_sympy_expr(expr1)
    formal2 = adapt_sympy_expr(expr2)

    s1a = formal1.format(rules={'Power': {'negative': 'sup'}})
    s1b = formal1.format(rules={'Power': {'negative': 'frac'}})
    s1c = formal1.format(rules={'Power': {'negative': 'inline'}})
    check(s1a, 'x^{-1}')
    check(s1b, r'\frac{1}{x}')
    check(s1c, '1/x')

    print()

    s2a = formal2.format(rules={'Power': {'negative': 'sup'}})
    s2b = formal2.format(rules={'Power': {'negative': 'frac'}})
    s2c = formal2.format(rules={'Power': {'negative': 'inline'}})
    check(s2a, 'x^{-2}')
    check(s2b, r'\frac{1}{x^{2}}')
    check(s2c, '1/x^{2}')
