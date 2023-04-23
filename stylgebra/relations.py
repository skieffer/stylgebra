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

from stylgebra.basic import *


class InvertibleInfix:

    def __init__(self, function, valence=True):
        self.function = function
        self.valence = valence

    def __ror__(self, L):
        if isinstance(L, FormalInfixRelation):
            f = lambda R: L.toChain().extended([self, R])
        elif isinstance(L, FormalRelnChain):
            f = lambda R: L.extended([self, R])
        else:
            f = lambda R: self.function(L, R, valence=self.valence)
        return InvertibleInfix(f, self.valence)

    def __or__(self, R):
        return self.function(R)

    def __invert__(self):
        return InvertibleInfix(self.function, valence=not self.valence)


class FormalRelation(Formal):

    pass


class FormalBinaryRelation(FormalRelation):

    pass


class FormalInfixRelation(FormalBinaryRelation):

    def __init__(self, left, right, valence=True, name=None, id=None):
        super().__init__(name=name, id=id)
        self.left = wrap(left)
        self.right = wrap(right)
        self.valence = valence
        self.symbol = None
        self.nsymbol = None
        self.phrase = None
        self.nphrase = None
        # The "bar op" should be a reference to the InvertibleInfix instance
        # we define for each subclass of FormalInfixRelation. It is so called
        # because it is an operator used by surrounding it with vert bars: |.|
        self.barOp = None

    def toChain(self):
        return FormalRelnChain([self.left, self.barOp, self.right])

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        options:

            omit-left: boolean
                Default: False
                If True, omit the lefthand term, but do prepend a space.
                This is useful for relation chains.

        subpaths:

            left: self.left
            right: self.right
        """
        form = mode.get('form')
        if form is None:
            if (self.valence and self.symbol is not None) or (not self.valence and self.nsymbol is not None):
                form = FormOpt.SYMBOLIC
            elif (self.valence and self.phrase is not None) or (not self.valence and self.nphrase is not None):
                form = FormOpt.VERBAL
            else:
                form = FormOpt.NAME

        if form == FormOpt.NAME:
            return MM(self.name())
        elif form == FormOpt.VALUE:
            # What would this mean? Decide whether the relation is true or false?
            raise NotImplementedError()

        left = '' if mode.get('omit-left') else self.fwd(self.left, 'left', rules, path)
        right = self.fwd(self.right, 'right', rules, path)

        if form == FormOpt.SYMBOLIC:
            return self.symbolic(mode, left, right)
        else:
            assert form == FormOpt.VERBAL
            return self.verbal(mode, left, right)

    def symbolic(self, mode, left, right):
        symb = self.symbol if self.valence else self.nsymbol
        return left + MM(f' {symb} ') + right

    def verbal(self, mode, left, right):
        phrase = self.phrase if self.valence else self.nphrase
        return left + f' {phrase} ' + right


class FormalSetMembershipRelation(FormalInfixRelation):

    def __init__(self, left, right, valence=True, name=None, id=None):
        if isinstance(right, list) or isinstance(right, set):
            # You can get away with passing a python list or set;
            # we will convert it into a FormalSet for you.
            from stylgebra.expressions import FormalSet
            right = FormalSet(elements=list(right))
        super().__init__(left, right, valence, name, id)
        self.symbol = r'\in'
        self.nsymbol = r'\not\in'
        self.phrase = 'is an element of'  # what about 'belongs to'? Should it be configurable?
        self.nphrase = 'is not an element of'
        self.barOp = in_


in_ = InvertibleInfix(FormalSetMembershipRelation)


class FormalLeqRelation(FormalInfixRelation):

    def __init__(self, left, right, valence=True, name=None, id=None):
        super().__init__(left, right, valence, name, id)
        self.symbol = r'\leq'
        self.nsymbol = r'\not\leq'
        self.phrase = 'is less than or equal to'
        self.nphrase = 'is not less than or equal to'
        self.barOp = leq


leq = InvertibleInfix(FormalLeqRelation)


class FormalLtRelation(FormalInfixRelation):

    def __init__(self, left, right, valence=True, name=None, id=None):
        super().__init__(left, right, valence, name, id)
        self.symbol = r'<'
        self.nsymbol = r'\nless'
        self.phrase = 'is less than'
        self.nphrase = 'is not less than'
        self.barOp = lt


lt = InvertibleInfix(FormalLtRelation)


class FormalRelnChain(Formal):
    """
    Represents a chain of terms and infix relations.
    The relations need not all be the same.
    """

    def __init__(self, chain):
        """
        :param chain: list of alternating formal terms and FormalInfixRelations,
            starting and ending with terms.
        """
        super().__init__()
        self.chain = chain

    def extend(self, ext):
        """
        Extend this chain in-place.
        """
        self.chain.extend(ext)

    def extended(self, ext):
        """
        Return a new instance, whose chain equals this one plus an extension.
        """
        return FormalRelnChain(self.chain + ext)

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        """
        subpaths:

            left: the leftmost term
            reln%d % i: the ith Infix relation for i from 1 to n - 1 when we have n terms.
        """
        chain = self.chain
        m = len(chain)
        assert m % 2 == 1
        n = (m - 1) // 2
        assert n > 0
        left = chain[0]
        s = self.fwd(left, 'left', rules, path)
        mod = {
            'omit-left': True
        }
        for i in range(n):
            reln, right = chain[2*i+1:2*i+3]
            ir = left |reln| right
            subpath = 'reln%d' % i
            s += self.fwd(ir, subpath, rules, path, modifier=mod)
            left = right
        return s

##############################################################################
# Tests


def try00():
    from stylgebra.expressions import FormalVariable
    a = FormalVariable('a')
    b = FormalVariable('b')
    c = FormalVariable('c')
    d = FormalVariable('d')
    rc = a |lt| b |leq| c |in_| d
    print(rc.format())


if __name__ == "__main__":
    try00()
