"""
 This file is part of nucypher.

 nucypher is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 nucypher is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with nucypher.  If not, see <https://www.gnu.org/licenses/>.
"""

import pytest

from nucypher.policy.conditions.lingo import ReturnValueTest


def test_return_result_test_simple():
    # >
    test = ReturnValueTest(comparator='>', value=0)
    assert test.eval(1)
    assert not test.eval(0)
    assert not test.eval(-1)

    # >=
    test = ReturnValueTest(comparator=">=", value=0)
    assert test.eval(2)
    assert test.eval(0)
    assert not test.eval(-2)

    # <
    test = ReturnValueTest(comparator="<", value=0)
    assert not test.eval(3)
    assert not test.eval(0)
    assert test.eval(-3)

    # <=
    test = ReturnValueTest(comparator="<=", value=0)
    assert not test.eval(3)
    assert test.eval(0)
    assert test.eval(-3)

    # ==
    test = ReturnValueTest(comparator="==", value=0)
    assert not test.eval(1)
    assert test.eval(0)
    assert not test.eval(-2)

    # !=
    test = ReturnValueTest(comparator="!=", value=0)
    assert test.eval(1)
    assert not test.eval(0)
    assert test.eval(-2)


def test_return_value_sanitization():
    with pytest.raises(ValueError):
        _test = ReturnValueTest('DROP', 'TABLE')
