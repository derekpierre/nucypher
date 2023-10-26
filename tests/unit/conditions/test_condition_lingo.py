import json

import pytest
from packaging.version import parse as parse_version

import nucypher
from nucypher.blockchain.eth.constants import NULL_ADDRESS
from nucypher.policy.conditions.context import USER_ADDRESS_CONTEXT
from nucypher.policy.conditions.exceptions import (
    InvalidConditionLingo,
)
from nucypher.policy.conditions.lingo import ConditionLingo, ConditionType
from tests.constants import TESTERCHAIN_CHAIN_ID


@pytest.fixture(scope="module")
def lingo_with_condition():
    return {
        "conditionType": ConditionType.TIME.value,
        "returnValueTest": {"value": 0, "comparator": ">"},
        "method": "blocktime",
        "chain": TESTERCHAIN_CHAIN_ID,
    }


@pytest.fixture(scope="module")
def lingo_with_compound_conditions(get_random_checksum_address):
    return {
        "version": ConditionLingo.VERSION,
        "condition": {
            "conditionType": ConditionType.COMPOUND.value,
            "operator": "and",
            "operands": [
                {
                    "conditionType": ConditionType.TIME.value,
                    "returnValueTest": {"value": 0, "comparator": ">"},
                    "method": "blocktime",
                    "chain": TESTERCHAIN_CHAIN_ID,
                },
                {
                    "conditionType": ConditionType.CONTRACT.value,
                    "chain": TESTERCHAIN_CHAIN_ID,
                    "method": "isPolicyActive",
                    "parameters": [":hrac"],
                    "returnValueTest": {"comparator": "==", "value": True},
                    "contractAddress": get_random_checksum_address(),
                    "functionAbi": {
                        "type": "function",
                        "name": "isPolicyActive",
                        "stateMutability": "view",
                        "inputs": [
                            {
                                "name": "_policyID",
                                "type": "bytes16",
                                "internalType": "bytes16",
                            }
                        ],
                        "outputs": [
                            {"name": "", "type": "bool", "internalType": "bool"}
                        ],
                    },
                },
                {
                    "conditionType": ConditionType.COMPOUND.value,
                    "operator": "or",
                    "operands": [
                        {
                            "conditionType": ConditionType.TIME.value,
                            "returnValueTest": {"value": 0, "comparator": ">"},
                            "method": "blocktime",
                            "chain": TESTERCHAIN_CHAIN_ID,
                        },
                        {
                            "conditionType": ConditionType.RPC.value,
                            "chain": TESTERCHAIN_CHAIN_ID,
                            "method": "eth_getBalance",
                            "parameters": [get_random_checksum_address(), "latest"],
                            "returnValueTest": {
                                "comparator": ">=",
                                "value": 10000000000000,
                            },
                        },
                    ],
                },
                {
                    "conditionType": ConditionType.COMPOUND.value,
                    "operator": "not",
                    "operands": [
                        {
                            "conditionType": ConditionType.TIME.value,
                            "returnValueTest": {"value": 0, "comparator": ">"},
                            "method": "blocktime",
                            "chain": TESTERCHAIN_CHAIN_ID,
                        },
                    ],
                },
            ],
        },
    }


def test_invalid_condition():
    # no version or condition
    with pytest.raises(InvalidConditionLingo):
        ConditionLingo.from_dict({})

    # no condition
    with pytest.raises(InvalidConditionLingo):
        ConditionLingo.from_dict({"version": ConditionLingo.VERSION})

    # invalid condition
    with pytest.raises(InvalidConditionLingo):
        ConditionLingo.from_dict(
            {
                "version": ConditionLingo.VERSION,
                "condition": {"dont_mind_me": "nothing_to_see_here"},
            }
        )

    # invalid operator
    invalid_operator = {
        "version": ConditionLingo.VERSION,
        "condition": {
            "conditionType": ConditionType.COMPOUND.value,
            "operator": "xTrue",
            "operands": [
                {
                    "conditionType": ConditionType.TIME.value,
                    "returnValueTest": {"value": 0, "comparator": ">"},
                    "method": "blocktime",
                    "chain": TESTERCHAIN_CHAIN_ID,
                },
            ],
        },
    }
    with pytest.raises(InvalidConditionLingo):
        ConditionLingo.from_dict(invalid_operator)

    # < 2 operands for and condition
    invalid_and_operands_lingo = {
        "version": ConditionLingo.VERSION,
        "condition": {
            "conditionType": ConditionType.COMPOUND.value,
            "operator": "and",
            "operands": [
                {
                    "conditionType": ConditionType.TIME.value,
                    "returnValueTest": {"value": 0, "comparator": ">"},
                    "method": "blocktime",
                    "chain": TESTERCHAIN_CHAIN_ID,
                }
            ],
        },
    }
    with pytest.raises(InvalidConditionLingo):
        ConditionLingo.from_dict(invalid_and_operands_lingo)

    # < 2 operands for or condition
    invalid_or_operands_lingo = {
        "version": ConditionLingo.VERSION,
        "condition": {
            "conditionType": ConditionType.COMPOUND.value,
            "operator": "or",
            "operands": [
                {
                    "conditionType": ConditionType.TIME.value,
                    "returnValueTest": {"value": 0, "comparator": ">"},
                    "method": "blocktime",
                    "chain": TESTERCHAIN_CHAIN_ID,
                }
            ],
        },
    }
    with pytest.raises(InvalidConditionLingo):
        ConditionLingo.from_dict(invalid_or_operands_lingo)

    # > 1 operand for `not` condition
    invalid_not_operands_lingo = {
        "version": ConditionLingo.VERSION,
        "condition": {
            "conditionType": ConditionType.COMPOUND.value,
            "operator": "not",
            "operands": [
                {
                    "conditionType": ConditionType.TIME.value,
                    "returnValueTest": {"value": 0, "comparator": ">"},
                    "method": "blocktime",
                    "chain": TESTERCHAIN_CHAIN_ID,
                },
                {
                    "conditionType": ConditionType.TIME.value,
                    "returnValueTest": {"value": 99999999999999999, "comparator": "<"},
                    "method": "blocktime",
                    "chain": TESTERCHAIN_CHAIN_ID,
                },
            ],
        },
    }
    with pytest.raises(InvalidConditionLingo):
        ConditionLingo.from_dict(invalid_not_operands_lingo)


@pytest.mark.parametrize("case", ["major", "minor", "patch"])
def test_invalid_condition_version(case):
    # version in the future
    current_version = parse_version(ConditionLingo.VERSION)
    major = current_version.major
    minor = current_version.minor
    patch = current_version.micro
    if case == "major":
        major += 1
    elif case == "minor":
        minor += 1
    else:
        patch += 1

    newer_version_string = f"{major}.{minor}.{patch}"
    lingo_dict = {
        "version": newer_version_string,
        "condition": {
            "conditionType": ConditionType.TIME.value,
            "returnValueTest": {"value": 0, "comparator": ">"},
            "method": "blocktime",
            "chain": TESTERCHAIN_CHAIN_ID,
        },
    }
    if case == "major":
        # exception should be thrown since incompatible:
        with pytest.raises(InvalidConditionLingo):
            ConditionLingo.from_dict(lingo_dict)
    else:
        # no exception thrown
        ConditionLingo.validate_condition_lingo(lingo_dict)
        _ = ConditionLingo.from_dict(lingo_dict)


def test_condition_lingo_to_from_dict(lingo_with_compound_conditions):
    clingo = ConditionLingo.from_dict(lingo_with_compound_conditions)
    clingo_dict = clingo.to_dict()
    assert clingo_dict == lingo_with_compound_conditions


def test_condition_lingo_to_from_json(lingo_with_compound_conditions):
    # A bit more convoluted because fields aren't
    # necessarily ordered - so string comparison is tricky
    clingo_from_dict = ConditionLingo.from_dict(lingo_with_compound_conditions)
    lingo_json = clingo_from_dict.to_json()

    clingo_from_json = ConditionLingo.from_json(lingo_json)
    assert clingo_from_json.to_dict() == lingo_with_compound_conditions


def test_condition_lingo_repr(lingo_with_compound_conditions):
    clingo = ConditionLingo.from_dict(lingo_with_compound_conditions)
    clingo_string = f"{clingo}"
    assert f"{clingo.__class__.__name__}" in clingo_string
    assert f"version={ConditionLingo.VERSION}" in clingo_string
    assert f"id={clingo.id}" in clingo_string
    assert f"size={len(bytes(clingo))}" in clingo_string


def test_lingo_parameter_int_type_preservation(custom_abi_with_multiple_parameters, mocker):
    mocker.patch.dict(
        nucypher.policy.conditions.context._DIRECTIVES,
        {USER_ADDRESS_CONTEXT: lambda: NULL_ADDRESS},
    )
    clingo_json = json.dumps(
        {
            "version": ConditionLingo.VERSION,
            "condition": json.loads(
                custom_abi_with_multiple_parameters  # fixture is already a json string
            ),
        }
    )

    clingo = ConditionLingo.from_json(clingo_json)
    conditions = clingo.to_dict()
    assert conditions["condition"]["parameters"][2] == 4


def test_lingo_resolves_condition_type(lingo_with_condition):
    for condition_type in ConditionType.values():
        lingo_with_condition["conditionType"] = condition_type
        ConditionLingo.resolve_condition_class(lingo_with_condition)


def test_lingo_rejects_invalid_condition_type(lingo_with_condition):
    for condition_type in ["invalid", "", None]:
        lingo_with_condition["conditionType"] = condition_type
        with pytest.raises(InvalidConditionLingo):
            ConditionLingo.resolve_condition_class(lingo_with_condition)
