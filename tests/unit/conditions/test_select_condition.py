import random

import pytest

from nucypher.policy.conditions.base import Condition
from nucypher.policy.conditions.exceptions import (
    InvalidCondition,
)
from nucypher.policy.conditions.lingo import ConditionType, ReturnValueTest
from nucypher.policy.conditions.select import SelectCase, SelectCondition
from nucypher.policy.conditions.utils import ConditionProviderManager


@pytest.fixture(scope="function")
def mock_conditions(mocker):
    cond_1 = mocker.Mock(spec=Condition)
    cond_1.verify.return_value = (True, 1)
    cond_1.to_dict.return_value = {"value": 1}

    cond_2 = mocker.Mock(spec=Condition)
    cond_2.verify.return_value = (True, 2)
    cond_2.to_dict.return_value = {"value": 2}

    cond_3 = mocker.Mock(spec=Condition)
    cond_3.verify.return_value = (True, 3)
    cond_3.to_dict.return_value = {"value": 3}

    return cond_1, cond_2, cond_3


def test_invalid_sequential_condition(rpc_condition, time_condition):
    valid_cases = [
        SelectCase(
            test=ReturnValueTest(comparator="==", value=0), condition=rpc_condition
        ),
        SelectCase(
            test=ReturnValueTest(comparator="==", value=1), condition=time_condition
        ),
    ]

    # invalid condition type
    with pytest.raises(InvalidCondition, match=ConditionType.SELECT.value):
        _ = SelectCondition(
            condition_type=ConditionType.TIME.value,
            value=":someVar",
            cases=valid_cases,
        )

    # value is not context var
    with pytest.raises(
        InvalidCondition, match="Invalid value; expected a context variable"
    ):
        _ = SelectCondition(
            condition_type=ConditionType.SELECT.value,
            value="not_a_context_variable",
            cases=valid_cases,
        )

    # no cases
    with pytest.raises(InvalidCondition, match="At least 2 cases are required"):
        _ = SelectCondition(
            condition_type=ConditionType.SELECT.value,
            value=":someVar",
            cases=[],
        )

    # only one case
    with pytest.raises(InvalidCondition, match="At least 2 cases are required"):
        _ = SelectCondition(
            condition_type=ConditionType.SELECT.value,
            value=":someVar",
            cases=[
                SelectCase(
                    test=ReturnValueTest(comparator="==", value=0),
                    condition=rpc_condition,
                ),
            ],
        )

    # invalid default condition
    with pytest.raises(InvalidCondition, match="Cannot resolve condition lingo"):
        _ = SelectCondition(
            condition_type=ConditionType.SELECT.value,
            value=":someVar",
            cases=valid_cases,
            default_condition={
                "random_field": "random_value",
            },  # invalid condition
        )

    # too many nested select conditions
    select_condition = SelectCondition(
        condition_type=ConditionType.SELECT.value,
        value=":someVar",
        cases=valid_cases,
    )

    nested_select_condition = SelectCondition(
        condition_type=ConditionType.SELECT.value,
        value=":someVar",
        cases=valid_cases,
        default_condition=select_condition,
    )

    double_nested_select_condition = SelectCondition(
        condition_type=ConditionType.SELECT.value,
        value=":someVar",
        cases=valid_cases,
        default_condition=nested_select_condition,
    )

    # nested at default condition
    with pytest.raises(InvalidCondition, match="Too many nested select conditions"):
        _ = SelectCondition(
            condition_type=ConditionType.SELECT.value,
            value=":someVar",
            cases=valid_cases,
            default_condition=double_nested_select_condition,
        )

    # nested in cases
    with pytest.raises(InvalidCondition, match="Too many nested select conditions"):
        _ = SelectCondition(
            condition_type=ConditionType.SELECT.value,
            value=":someVar",
            cases=[
                SelectCase(
                    test=ReturnValueTest(comparator="==", value=1),
                    condition=time_condition,
                ),
                SelectCase(
                    test=ReturnValueTest(comparator="==", value=0),
                    condition=double_nested_select_condition,
                ),
            ],
        )


def test_select_condition_repr(rpc_condition, time_condition):
    context_var = ":someVar"
    # no default condition
    select_condition = SelectCondition(
        condition_type=ConditionType.SELECT.value,
        value=context_var,
        cases=[
            SelectCase(
                test=ReturnValueTest(comparator="==", value=0), condition=rpc_condition
            ),
            SelectCase(
                test=ReturnValueTest(comparator="==", value=1), condition=time_condition
            ),
        ],
    )
    select_condition_str = str(select_condition)
    assert select_condition.__class__.__name__ in select_condition_str
    assert f"value={context_var}" in select_condition_str
    assert "num_cases=2" in select_condition_str
    assert "default_condition=None" in select_condition_str

    # default condition
    select_condition = SelectCondition(
        condition_type=ConditionType.SELECT.value,
        value=context_var,
        cases=[
            SelectCase(
                test=ReturnValueTest(comparator="==", value=0), condition=rpc_condition
            ),
            SelectCase(
                test=ReturnValueTest(comparator="==", value=1), condition=time_condition
            ),
        ],
        default_condition=rpc_condition,
    )
    select_condition_str = str(select_condition)
    assert select_condition.__class__.__name__ in select_condition_str
    assert f"value={context_var}" in select_condition_str
    assert "num_cases=2" in select_condition_str
    assert f"default_condition={str(rpc_condition)}" in select_condition_str


@pytest.mark.usefixtures("mock_skip_schema_validation")
def test_select_condition_no_default_condition(mocker, mock_conditions):
    cond_1, cond_2, cond_3 = mock_conditions

    cond_1.verify.return_value = (True, 1)
    cond_2.verify.return_value = (False, 2)
    cond_3.verify.return_value = (True, 3)

    select_condition = SelectCondition(
        condition_type=ConditionType.SELECT.value,
        value=":someVar",
        cases=[
            SelectCase(
                test=ReturnValueTest(comparator="==", value=1), condition=cond_1
            ),
            SelectCase(
                test=ReturnValueTest(comparator="==", value=2), condition=cond_2
            ),
            SelectCase(
                test=ReturnValueTest(comparator="==", value=3), condition=cond_3
            ),
        ],
    )

    condition_provider_manager = ConditionProviderManager({})

    # case 1
    context = {":someVar": 1}
    result = select_condition.verify(providers=condition_provider_manager, **context)
    assert result == (True, 1)

    # case 2
    context = {":someVar": 2}
    result = select_condition.verify(providers=condition_provider_manager, **context)
    assert result == (False, 2)

    # case 3
    context = {":someVar": 3}
    result = select_condition.verify(providers=condition_provider_manager, **context)
    assert result == (True, 3)

    # default case (no default condition)
    context = {":someVar": 4}
    result = select_condition.verify(providers=condition_provider_manager, **context)
    assert result == (False, None)


@pytest.mark.usefixtures("mock_skip_schema_validation")
def test_select_condition_default_condition(mocker, mock_conditions):
    cond_1, cond_2, cond_3 = mock_conditions

    cond_1.verify.return_value = (True, 1)
    cond_2.verify.return_value = (False, 2)
    cond_3.verify.return_value = (True, 120)

    select_condition = SelectCondition(
        condition_type=ConditionType.SELECT.value,
        value=":someVar",
        cases=[
            SelectCase(
                test=ReturnValueTest(comparator="==", value=1), condition=cond_1
            ),
            SelectCase(
                test=ReturnValueTest(comparator="==", value=2), condition=cond_2
            ),
        ],
        default_condition=cond_3,
    )

    condition_provider_manager = ConditionProviderManager({})

    # case 1
    context = {":someVar": 1}
    result = select_condition.verify(providers=condition_provider_manager, **context)
    assert result == (True, 1)

    # case 2
    context = {":someVar": 2}
    result = select_condition.verify(providers=condition_provider_manager, **context)
    assert result == (False, 2)

    # default case
    for i in range(10):
        value = random.randint(3, 1000)
        if i % 2 == 0:
            value = -value

        context = {":someVar": value}
        result = select_condition.verify(
            providers=condition_provider_manager, **context
        )
        assert result == (True, 120)

    # mismatched type case; string instead of int
    context = {":someVar": "string_value_instead_of_int"}
    result = select_condition.verify(providers=condition_provider_manager, **context)
    assert result == (True, 120)

    # mismatched type case; float instead of int
    context = {":someVar": 1.20}
    result = select_condition.verify(providers=condition_provider_manager, **context)
    assert result == (True, 120)

    # mismatched type case; hex bytes
    context = {":someVar": "0xdeadbeef"}
    result = select_condition.verify(providers=condition_provider_manager, **context)
    assert result == (True, 120)

    # TODO note that a bool value of "True" evaluates to 1 which matches the
    #  first case - is that a concern?

    # back to case 2
    context = {":someVar": 2}
    result = select_condition.verify(providers=condition_provider_manager, **context)
    assert result == (False, 2)


@pytest.mark.usefixtures("mock_skip_schema_validation")
def test_select_condition_failure_propagated(mock_conditions):
    cond_1, cond_2, cond_3 = mock_conditions

    cond_1.verify.side_effect = Exception("Condition 1 failed")
    cond_2.verify.side_effect = Exception("Condition 2 failed")
    cond_3.verify.side_effect = Exception("Condition 3 failed")

    select_condition = SelectCondition(
        condition_type=ConditionType.SELECT.value,
        value=":someVar",
        cases=[
            SelectCase(
                test=ReturnValueTest(comparator="==", value=1), condition=cond_1
            ),
            SelectCase(
                test=ReturnValueTest(comparator="==", value=2), condition=cond_2
            ),
        ],
        default_condition=cond_3,
    )

    condition_provider_manager = ConditionProviderManager({})

    # case 1 raises
    with pytest.raises(Exception, match="Condition 1 failed"):
        context = {":someVar": 1}
        _ = select_condition.verify(providers=condition_provider_manager, **context)

    # case 2 raises
    with pytest.raises(Exception, match="Condition 2 failed"):
        context = {":someVar": 2}
        _ = select_condition.verify(providers=condition_provider_manager, **context)

    # default condition raises
    with pytest.raises(Exception, match="Condition 3 failed"):
        context = {":someVar": 100_000_000}
        _ = select_condition.verify(providers=condition_provider_manager, **context)
