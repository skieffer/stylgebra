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


class bcolors:
    """
    See <https://stackoverflow.com/a/287944>
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def check(a, e, do_assert=True):
    """
    Check an "actual" string (a) against an "expected" string (e).
    """
    if do_assert:
        if str(a) != e:
            print(f'{bcolors.FAIL}{a}{bcolors.ENDC}')
            print(bcolors.OKGREEN + e + bcolors.ENDC)
        else:
            print(a)
        assert str(a) == e
    else:
        print(a)
        print("    ASSERTION SKIPPED")
