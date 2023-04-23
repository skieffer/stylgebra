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

import random
from fractions import Fraction


def nice_random_integer(
        digit_lh = (0.5, 0.5),
        negative_lh = 0.5,
        zero_ok = True):
    """
    Generate a "nice random" integer.

    This is for use when generating examples of structures that involve
    integers, and it is meant to make the kinds of decisions you
    would probably make while writing down examples on a chalkboard:

    You would choose both positive and negative numbers; the numbers would
    not be terribly large. This is what "nice" means.

    In the parameters, an "lh" suffix means "liklihood".

    :param digit_lh: pass a tuple of floats summing to unity. These are the
        liklihoods, respectively, of the number we generate having 1, 2, 3, ... digits.
        For example the default value of (0.5, 0.5) means that half the time we
        will generate a 1-digit number, and the other half a 2-digit number.
    :param negative_lh: liklihood of the number being negative
    :param zero_ok: if False, we will not return zero

    :return: int
    """
    # Decide how many digits the number will be.
    d = random.choices(range(1, len(digit_lh) + 1), weights=digit_lh)[0]

    # Compute the closed-open interval [a, b) from which the integer will be chosen.
    b = 10**d
    a = 0 if (d == 1 and zero_ok) else b/10

    n = random.randrange(a, b)
    if random.random() < negative_lh:
        n *= -1

    return n


def nice_random_rational(
        integer_lh = 0.5,
        digit_lh = (0.5, 0.5),
        negative_lh = 0.5,
        zero_ok = True
    ):
    """
    Generate a "nice random" rational number.

    This function simply builds off the one that generates "nice random" integers,
    and again is meant to generate pseudo-random rational numbers of the kind
    you would tend to write down at the chalkboard.

    You would choose both positive and negative numbers; several would
    be pure integers (to illustrate that that's okay); neither numerator
    nor denominator would ever be terribly large. This is what "nice" means.

    In the parameters, an "lh" suffix means "liklihood".
    Note, however, that these tend to be only approximate liklihoods in the
    end, due to a final step of reducing to least terms.

    Thus, e.g., we will start out deciding on a pure integer or proper rational
    number based on the `integer_lh` parameter. However, over time you will
    get slightly more pure integers than you asked for, since e.g. we may
    generate 10/2 and then return 5 after reducing.

    :param integer_lh: liklihood of the number being a pure integer.
    :param digit_lh: as in `nice_random_integer`
    :param negative_lh: as in `nice_random_integer`
    :param zero_ok: as in `nice_random_integer`

    :return: instance of Python's fractions.Fraction class
    """
    # Numerator:
    n = nice_random_integer(digit_lh=digit_lh, negative_lh=negative_lh, zero_ok=zero_ok)

    # Denominator:
    d = 1
    if n != 0 and random.random() >= integer_lh:
        d = nice_random_integer(digit_lh=digit_lh, negative_lh=0, zero_ok=False)

    return Fraction(n, d)
