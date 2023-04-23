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

from sympy.core import (
    S, Symbol, Add, Mul, Pow,
    Integer, Rational,
)

from stylgebra.excep import FormalExcep
from stylgebra.expressions import *


class SymPyExprVisitor:

    def __init__(self):
        pass

    def visit(self, expr):
        expr_name = expr.func.__name__
        method_name = f'visit_{expr_name}'
        method = getattr(self, method_name)
        if method is None:
            msg = f'Sorry, no visitor method yet for Expr of type {expr_name}'
            raise FormalExcep(msg)
        return method(expr)

    def visit_NegativeOne(self, expr):
        return self.visit_Integer(expr)

    def visit_Symbol(self, expr):
        assert isinstance(expr, Symbol)
        return FormalVariable(expr.name)

    def visit_Integer(self, expr):
        assert isinstance(expr, Integer)
        return FormalInteger(value=int(expr))

    def visit_Rational(self, expr):
        assert isinstance(expr, Rational)
        return formalQuoFromFrac(expr)

    def visit_Add(self, expr):
        assert isinstance(expr, Add)
        return FormalSum(terms=[
            self.visit(term) for term in expr.args
        ])

    def visit_Mul(self, expr):
        assert isinstance(expr, Mul)
        args = expr.args

        if len(args) == 2 and args[0] == S.NegativeOne:
            term = self.visit(args[1])
            return FormalSummand(term, sign=-1)

        upstairs = []
        downstairs = []
        for arg in args:
            if isinstance(arg, Pow) and arg.args[1] < 0:
                inverse = Pow(arg.base, -arg.exp)
                downstairs.append(self.visit(inverse))
            else:
                upstairs.append(self.visit(arg))

        def handle_factor_list(factors):
            if len(factors) > 1:
                return FormalProduct(factors=factors)
            elif factors:
                return factors[0]
            else:
                return self.visit(S(1))

        u = handle_factor_list(upstairs)
        if downstairs:
            d = handle_factor_list(downstairs)
            return FormalQuotient(u, d)
        else:
            return u

    def visit_Pow(self, expr):
        assert isinstance(expr, Pow)
        b = self.visit(expr.base)
        e = self.visit(expr.exp)
        return FormalPower(b, e)


def adapt_sympy_expr(expr):
    """
    Turn a SymPy Expr into one of our formal class instances.

    :param expr: a sympy Expr instance
    :return: a Formal instance
    """
    visitor = SymPyExprVisitor()
    formal = visitor.visit(expr)
    return formal
