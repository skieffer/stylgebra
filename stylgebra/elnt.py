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

from sympy import primitive_root, totient, igcd, isprime, FF

from stylgebra.basic import *
from stylgebra.excep import FormalExcep


class FormalIntResidue(Formal):

    def __init__(self, r, m, name=None, id=None):
        super().__init__(name=name, id=id)
        if not isprime(m):
            raise FormalExcep(f'FormalIntResidue not yet supported for non-prime modulus {m}')
        self.modulus = m
        self.residue = r
        self.ring = FF(m)
        self.value(self.ring(r))

    @withmode
    def format(self, mode=None, rules=None, path=None, modifier=None):
        form = mode.get('form')
        if form is None:
            if self.name() is not None:
                form = FormOpt.NAME
            else:
                form = FormOpt.VALUE

        if form == FormOpt.NAME:
            return MM(self.name())
        elif form == FormOpt.VALUE:
            #return MM(self.value())
            return MM(int(self.value()))


def pick_primitive_root(modulus, auto_power=0):
    """
    You can easily get a primitive root r for a given modulus m using
    SymPy's `primitive_root` function. But you always get the same one.
    This function provides a convenient way to get the others.

    If g is the generator returned by `primitive_root`, and if r is
    the list of all units mod phi(modulus), then if you pass auto_power = k
    you will get the r[k] power of g.

    Example:
        If modulus == 13, then g = primitive_root(13) == 2.
        The available powers are [1, 5, 7, 11] (units mod 12 == 13 - 1).

        auto_power      return
        0               2^1 == 2
        1               2^5 == 6
        2               2^7 == 11
        3               2^11 == 7
    """
    g = primitive_root(modulus)
    if auto_power > 0:
        t = totient(modulus)
        s = totient(t)
        a = auto_power % s
        u = 1
        while a > 0:
            if igcd(u, t) == 1:
                a -= 1
        g = g**u % modulus
    return g
