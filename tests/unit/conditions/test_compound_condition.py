import copy
import json
from typing import Any, List
from unittest.mock import Mock

import pytest
from marshmallow import post_load
from web3.providers import BaseProvider

from nucypher.policy.conditions.base import AccessControlCondition
from nucypher.policy.conditions.evm import ContractCondition
from nucypher.policy.conditions.exceptions import InvalidCondition
from nucypher.policy.conditions.lingo import (
    AndCompoundCondition,
    CompoundAccessControlCondition,
    ConditionType,
    NotCompoundCondition,
    OrCompoundCondition,
)


@pytest.fixture(scope="function")
def mock_conditions():
    condition_1 = Mock(spec=AccessControlCondition)
    condition_1.verify.return_value = (True, 1)
    condition_1.to_dict.return_value = {
        "value": 1
    }  # needed for "id" value calc for CompoundAccessControlCondition

    condition_2 = Mock(spec=AccessControlCondition)
    condition_2.verify.return_value = (True, 2)
    condition_2.to_dict.return_value = {"value": 2}

    condition_3 = Mock(spec=AccessControlCondition)
    condition_3.verify.return_value = (True, 3)
    condition_3.to_dict.return_value = {"value": 3}

    condition_4 = Mock(spec=AccessControlCondition)
    condition_4.verify.return_value = (True, 4)
    condition_4.to_dict.return_value = {"value": 4}

    return condition_1, condition_2, condition_3, condition_4


def test_invalid_compound_condition(time_condition, rpc_condition):
    for operator in CompoundAccessControlCondition.OPERATORS:
        if operator == CompoundAccessControlCondition.NOT_OPERATOR:
            operands = [time_condition]
        else:
            operands = [time_condition, rpc_condition]

        # invalid condition type
        with pytest.raises(InvalidCondition, match=ConditionType.COMPOUND.value):
            _ = CompoundAccessControlCondition(
                condition_type=ConditionType.TIME.value,
                operator=operator,
                operands=operands,
            )

    # invalid operator - 1 operand
    with pytest.raises(InvalidCondition):
        _ = CompoundAccessControlCondition(operator="5True", operands=[time_condition])

    # invalid operator - 2 operands
    with pytest.raises(InvalidCondition):
        _ = CompoundAccessControlCondition(
            operator="5True", operands=[time_condition, rpc_condition]
        )

    # no operands
    with pytest.raises(InvalidCondition):
        _ = CompoundAccessControlCondition(operator=operator, operands=[])

    # > 1 operand for not operator
    with pytest.raises(InvalidCondition):
        _ = CompoundAccessControlCondition(
            operator=CompoundAccessControlCondition.NOT_OPERATOR,
            operands=[time_condition, rpc_condition],
        )

    # < 2 operands for or operator
    with pytest.raises(InvalidCondition):
        _ = CompoundAccessControlCondition(
            operator=CompoundAccessControlCondition.OR_OPERATOR,
            operands=[time_condition],
        )

    # < 2 operands for and operator
    with pytest.raises(InvalidCondition):
        _ = CompoundAccessControlCondition(
            operator=CompoundAccessControlCondition.AND_OPERATOR,
            operands=[rpc_condition],
        )

    # exceeds max operands
    operands = list()
    for i in range(CompoundAccessControlCondition.MAX_OPERANDS + 1):
        operands.append(rpc_condition)
    with pytest.raises(InvalidCondition):
        _ = CompoundAccessControlCondition(
            operator=CompoundAccessControlCondition.OR_OPERATOR,
            operands=operands,
        )
    with pytest.raises(InvalidCondition):
        _ = CompoundAccessControlCondition(
            operator=CompoundAccessControlCondition.AND_OPERATOR,
            operands=operands,
        )


@pytest.mark.parametrize("operator", CompoundAccessControlCondition.OPERATORS)
def test_compound_condition_schema_validation(operator, time_condition, rpc_condition):
    if operator == CompoundAccessControlCondition.NOT_OPERATOR:
        operands = [time_condition]
    else:
        operands = [time_condition, rpc_condition]

    compound_condition = CompoundAccessControlCondition(
        operator=operator, operands=operands
    )
    compound_condition_dict = compound_condition.to_dict()

    # no issues here
    CompoundAccessControlCondition.validate(compound_condition_dict)

    # no issues with optional name
    compound_condition_dict["name"] = "my_contract_condition"
    CompoundAccessControlCondition.validate(compound_condition_dict)

    with pytest.raises(InvalidCondition):
        # incorrect condition type
        compound_condition_dict = compound_condition.to_dict()
        compound_condition_dict["condition_type"] = ConditionType.RPC.value
        CompoundAccessControlCondition.validate(compound_condition_dict)

    with pytest.raises(InvalidCondition):
        # invalid operator
        compound_condition_dict = compound_condition.to_dict()
        compound_condition_dict["operator"] = "5True"
        CompoundAccessControlCondition.validate(compound_condition_dict)

    with pytest.raises(InvalidCondition):
        # no operator
        compound_condition_dict = compound_condition.to_dict()
        del compound_condition_dict["operator"]
        CompoundAccessControlCondition.validate(compound_condition_dict)

    with pytest.raises(InvalidCondition):
        # no operands
        compound_condition_dict = compound_condition.to_dict()
        del compound_condition_dict["operands"]
        CompoundAccessControlCondition.validate(compound_condition_dict)


def test_and_condition_and_short_circuit(mock_conditions):
    condition_1, condition_2, condition_3, condition_4 = mock_conditions

    and_condition = AndCompoundCondition(
        operands=[
            condition_1,
            condition_2,
            condition_3,
            condition_4,
        ]
    )

    # ensure that all conditions evaluated when all return True
    result, value = and_condition.verify(providers={})
    assert result is True
    assert len(value) == 4, "all conditions evaluated"
    assert value == [1, 2, 3, 4]

    # ensure that short circuit happens when 1st condition is false
    condition_1.verify.return_value = (False, 1)
    result, value = and_condition.verify(providers={})
    assert result is False
    assert len(value) == 1, "only one condition evaluated"
    assert value == [1]

    # short circuit occurs for 3rd entry
    condition_1.verify.return_value = (True, 1)
    condition_3.verify.return_value = (False, 3)
    result, value = and_condition.verify(providers={})
    assert result is False
    assert len(value) == 3, "3-of-4 conditions evaluated"
    assert value == [1, 2, 3]


def test_or_condition_and_short_circuit(mock_conditions):
    condition_1, condition_2, condition_3, condition_4 = mock_conditions

    or_condition = OrCompoundCondition(
        operands=[
            condition_1,
            condition_2,
            condition_3,
            condition_4,
        ]
    )

    # ensure that only first condition evaluated when first is True
    condition_1.verify.return_value = (True, 1)  # short circuit here
    result, value = or_condition.verify(providers={})
    assert result is True
    assert len(value) == 1, "only first condition needs to be evaluated"
    assert value == [1]

    # ensure first True condition is returned
    condition_1.verify.return_value = (False, 1)
    condition_2.verify.return_value = (False, 2)
    condition_3.verify.return_value = (True, 3)  # short circuit here

    result, value = or_condition.verify(providers={})
    assert result is True
    assert len(value) == 3, "third condition causes short circuit"
    assert value == [1, 2, 3]

    # no short circuit occurs when all are False
    condition_1.verify.return_value = (False, 1)
    condition_2.verify.return_value = (False, 2)
    condition_3.verify.return_value = (False, 3)
    condition_4.verify.return_value = (False, 4)

    result, value = or_condition.verify(providers={})
    assert result is False
    assert len(value) == 4, "all conditions evaluated"
    assert value == [1, 2, 3, 4]


def test_compound_condition(mock_conditions):
    condition_1, condition_2, condition_3, condition_4 = mock_conditions

    compound_condition = AndCompoundCondition(
        operands=[
            OrCompoundCondition(
                operands=[
                    condition_1,
                    condition_2,
                    condition_3,
                ]
            ),
            condition_4,
        ]
    )

    # all conditions are True
    result, value = compound_condition.verify(providers={})
    assert result is True
    assert len(value) == 2, "or_condition and condition_4"
    assert value == [[1], 4]

    # or condition is False
    condition_1.verify.return_value = (False, 1)
    condition_2.verify.return_value = (False, 2)
    condition_3.verify.return_value = (False, 3)
    result, value = compound_condition.verify(providers={})
    assert result is False
    assert len(value) == 1, "or_condition"
    assert value == [
        [1, 2, 3]
    ]  # or-condition does not short circuit, but and-condition is short-circuited because or-condition is False

    # or condition is True but condition 4 is False
    condition_1.verify.return_value = (True, 1)
    condition_4.verify.return_value = (False, 4)

    result, value = compound_condition.verify(providers={})
    assert result is False
    assert len(value) == 2, "or_condition and condition_4"
    assert value == [
        [1],
        4,
    ]  # or-condition short-circuited because condition_1 was True

    # condition_4 is now true
    condition_4.verify.return_value = (True, 4)
    result, value = compound_condition.verify(providers={})
    assert result is True
    assert len(value) == 2, "or_condition and condition_4"
    assert value == [
        [1],
        4,
    ]  # or-condition short-circuited because condition_1 was True


def test_nested_compound_condition(mock_conditions):
    condition_1, condition_2, condition_3, condition_4 = mock_conditions

    nested_compound_condition = AndCompoundCondition(
        operands=[
            OrCompoundCondition(
                operands=[
                    condition_1,
                    AndCompoundCondition(
                        operands=[
                            condition_2,
                            condition_3,
                        ]
                    ),
                ]
            ),
            condition_4,
        ]
    )

    # all conditions are True
    result, value = nested_compound_condition.verify(providers={})
    assert result is True
    assert len(value) == 2, "or_condition and condition_4"
    assert value == [[1], 4]  # or short-circuited since condition_1 is True

    # set condition_1 to False so nested and-condition must be evaluated
    condition_1.verify.return_value = (False, 1)

    result, value = nested_compound_condition.verify(providers={})
    assert result is True
    assert len(value) == 2, "or_condition and condition_4"
    assert value == [
        [1, [2, 3]],
        4,
    ]  # nested and-condition was evaluated and evaluated to True

    # set condition_4 to False so that overall result flips to False
    condition_4.verify.return_value = (False, 4)
    result, value = nested_compound_condition.verify(providers={})
    assert result is False
    assert len(value) == 2, "or_condition and condition_4"
    assert value == [[1, [2, 3]], 4]


def test_not_compound_condition(mock_conditions):
    condition_1, condition_2, condition_3, condition_4 = mock_conditions

    not_condition = NotCompoundCondition(operand=condition_1)

    #
    # simple `not`
    #
    condition_1.verify.return_value = (True, 1)
    result, value = not_condition.verify(providers={})
    assert result is False
    assert value == 1

    condition_1.verify.return_value = (False, 2)
    result, value = not_condition.verify(providers={})
    assert result is True
    assert value == 2

    #
    # `not` of `or` condition
    #

    # only True
    condition_1.verify.return_value = (True, 1)
    condition_2.verify.return_value = (True, 2)
    condition_3.verify.return_value = (True, 3)

    or_condition = OrCompoundCondition(
        operands=[
            condition_1,
            condition_2,
            condition_3,
        ]
    )
    not_condition = NotCompoundCondition(operand=or_condition)
    or_result, or_value = or_condition.verify(providers={})
    result, value = not_condition.verify(providers={})
    assert result is False
    assert result is (not or_result)
    assert value == or_value

    # only False
    condition_1.verify.return_value = (False, 1)
    condition_2.verify.return_value = (False, 2)
    condition_3.verify.return_value = (False, 3)
    or_result, or_value = or_condition.verify(providers={})
    result, value = not_condition.verify(providers={})
    assert result is True
    assert result is (not or_result)
    assert value == or_value

    # mixture of True/False
    condition_1.verify.return_value = (False, 1)
    condition_2.verify.return_value = (False, 2)
    condition_3.verify.return_value = (True, 3)
    or_result, or_value = or_condition.verify(providers={})
    result, value = not_condition.verify(providers={})
    assert result is False
    assert result is (not or_result)
    assert value == or_value

    #
    # `not` of `and` condition
    #

    # only True
    condition_1.verify.return_value = (True, 1)
    condition_2.verify.return_value = (True, 2)
    condition_3.verify.return_value = (True, 3)

    and_condition = AndCompoundCondition(
        operands=[
            condition_1,
            condition_2,
            condition_3,
        ]
    )
    not_condition = NotCompoundCondition(operand=and_condition)

    and_result, and_value = and_condition.verify(providers={})
    result, value = not_condition.verify(providers={})
    assert result is False
    assert result is (not and_result)
    assert value == and_value

    # only False
    condition_1.verify.return_value = (False, 1)
    condition_2.verify.return_value = (False, 2)
    condition_3.verify.return_value = (False, 3)
    and_result, and_value = and_condition.verify(providers={})
    result, value = not_condition.verify(providers={})
    assert result is True
    assert result is (not and_result)
    assert value == and_value

    # mixture of True/False
    condition_1.verify.return_value = (False, 1)
    condition_2.verify.return_value = (True, 2)
    condition_3.verify.return_value = (False, 3)
    and_result, and_value = and_condition.verify(providers={})
    result, value = not_condition.verify(providers={})
    assert result is True
    assert result is (not and_result)
    assert value == and_value

    #
    # Complex nested `or` and `and` (reused nested compound condition in previous test)
    #
    nested_compound_condition = AndCompoundCondition(
        operands=[
            OrCompoundCondition(
                operands=[
                    condition_1,
                    AndCompoundCondition(
                        operands=[
                            condition_2,
                            condition_3,
                        ]
                    ),
                ]
            ),
            condition_4,
        ]
    )

    not_condition = NotCompoundCondition(operand=nested_compound_condition)

    # reset all conditions to True
    condition_1.verify.return_value = (True, 1)
    condition_2.verify.return_value = (True, 2)
    condition_3.verify.return_value = (True, 3)
    condition_4.verify.return_value = (True, 4)

    nested_result, nested_value = nested_compound_condition.verify(providers={})
    result, value = not_condition.verify(providers={})
    assert result is False
    assert result is (not nested_result)
    assert value == nested_value

    # set condition_1 to False so nested and-condition must be evaluated
    condition_1.verify.return_value = (False, 1)

    nested_result, nested_value = nested_compound_condition.verify(providers={})
    result, value = not_condition.verify(providers={})
    assert result is False
    assert result is (not nested_result)
    assert value == nested_value

    # set condition_4 to False so that overall result flips to False, so `not` is now True
    condition_4.verify.return_value = (False, 4)
    nested_result, nested_value = nested_compound_condition.verify(providers={})
    result, value = not_condition.verify(providers={})
    assert result is True
    assert result is (not nested_result)
    assert value == nested_value


def test_sequential_compound_condition(mock_conditions):
    condition_1, condition_2, condition_3, condition_4 = mock_conditions

    condition_1.verify.return_value = (True, 1)
    condition_2.verify = lambda providers, **context: (
        True,
        context[":compound_condition_1_result"] * 2,
    )
    condition_3.verify = lambda providers, **context: (
        True,
        context[":compound_condition_2_result"] * 2,
    )
    condition_4.verify = lambda providers, **context: (
        True,
        context[":compound_condition_3_result"] * 2,
    )

    # and condition
    and_condition = AndCompoundCondition(
        operands=[
            condition_1,
            condition_2,
            condition_3,
            condition_4,
        ]
    )
    result, value = and_condition.verify(providers={})
    assert result is True
    assert value == [1, 2, 4, 8]

    # nested and condition
    nested_and_condition = AndCompoundCondition(
        operands=[
            condition_1,
            AndCompoundCondition(
                operands=[
                    condition_2,
                    AndCompoundCondition(
                        operands=[
                            condition_3,
                            condition_4,
                        ]
                    ),
                ]
            ),
        ]
    )
    result, value = nested_and_condition.verify(providers={})
    assert result is True
    assert value == [1, [2, [4, 8]]]


class FakeExecutionContractCondition(ContractCondition):
    class Schema(ContractCondition.Schema):
        @post_load
        def make(self, data, **kwargs):
            return FakeExecutionContractCondition(**data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _execute_call(self, parameters: List[Any]) -> Any:
        return parameters[0] * 3

    def _configure_provider(self, provider: BaseProvider):
        return


def test_sequential_compound_contract_conditions():
    base_contract_condition = {
        "conditionType": "contract",
        "contractAddress": "0x01B67b1194C75264d06F808A921228a95C765dd7",
        "method": "tripleValue",
        "parameters": [],  # TBD
        "functionAbi": {
            "inputs": [
                {"internalType": "uint256", "name": "value", "type": "uint256"},
            ],
            "name": "tripleValue",
            "outputs": [
                {"internalType": "uint256", "name": "doubled", "type": "uint256"}
            ],
            "stateMutability": "view",
            "type": "function",
            "constant": True,
        },
        "chain": 137,
        "returnValueTest": {"comparator": "==", "value": 0},  # TBD
    }

    operands = []
    expected_results = []
    starting_value = 1
    current_expected_result = None
    for i in range(CompoundAccessControlCondition.MAX_OPERANDS):
        fake_condition_dict = copy.deepcopy(base_contract_condition)
        if i == 0:
            # first one
            fake_condition_dict["parameters"] = [starting_value]
            current_expected_result = starting_value * 3
        else:
            fake_condition_dict["parameters"] = [
                f":compound_condition_{i}_result"
            ]  # context var used for result
            current_expected_result = current_expected_result * 3

        fake_condition_dict["returnValueTest"] = {
            "comparator": "==",
            "value": current_expected_result,
        }
        expected_results.append(current_expected_result)

        fake_condition = FakeExecutionContractCondition.from_json(
            json.dumps(fake_condition_dict)
        )
        operands.append(fake_condition)

    fake_providers = {137: {Mock(BaseProvider)}}
    context = {"a": 1, "b": 2}
    original_context = dict(context)  # store copy to confirm context remained unchanged

    # OR compound condition, since true only first condition evaluated
    or_condition = OrCompoundCondition(operands=operands)
    result, value = or_condition.verify(providers=fake_providers, **context)
    assert result is True
    assert value == [starting_value * 3]
    assert context == original_context, "original context remains unchanged"

    # AND compound condition, results from prior condition passed to other condition
    and_condition = AndCompoundCondition(operands=operands)

    result, value = and_condition.verify(providers=fake_providers, **context)
    assert result is True
    assert value == expected_results
    assert context == original_context, "original context remains unchanged"

    # Nested AND compound condition
    nested_and_condition = AndCompoundCondition(
        operands=[
            operands[0],
            AndCompoundCondition(
                operands=[operands[1], AndCompoundCondition(operands=operands[2:])]
            ),
        ],
    )
    result, value = nested_and_condition.verify(
        providers=fake_providers, context=context
    )
    assert result is True
    assert value == [expected_results[0], [expected_results[1], expected_results[2:]]]
    assert context == original_context, "original context remains unchanged"
