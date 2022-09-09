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

import json
from pathlib import Path

import pytest
from web3 import Web3

import tests
from nucypher.policy.conditions.evm import ContractCondition, RPCCondition
from nucypher.policy.conditions.lingo import AND, OR, ConditionLingo, ReturnValueTest
from nucypher.policy.conditions.time import TimeCondition

VECTORS_FILE = Path(tests.__file__).parent / "data" / "test_conditions.json"

with open(VECTORS_FILE, 'r') as file:
    VECTORS = json.loads(file.read())


# ERC1155

@pytest.fixture()
def ERC1155_balance_condition_data():
    data = json.dumps(VECTORS['ERC1155_balance'])
    return data


@pytest.fixture()
def ERC1155_balance_condition(ERC1155_balance_condition_data):
    data = ERC1155_balance_condition_data
    condition = ContractCondition.from_json(data)
    return condition


# ERC20

@pytest.fixture()
def ERC20_balance_condition_data():
    data = json.dumps(VECTORS['ERC20_balance'])
    return data


@pytest.fixture()
def ERC20_balance_condition(ERC20_balance_condition_data):
    data = ERC20_balance_condition_data
    condition = ContractCondition.from_json(data)
    return condition


@pytest.fixture
def rpc_condition():
    condition = RPCCondition(
        method='eth_getBalance',
        chain='testerchain',
        return_value_test=ReturnValueTest('==', Web3.toWei(1_000_000, 'ether')),
        parameters=[
            ':userAddress'
        ]
    )
    return condition


@pytest.fixture
def evm_condition(test_registry):
    condition = ContractCondition(
        contract_address='0xadd9d957170DF6f33982001E4C22eCcDd5539118',
        method='balanceOf',
        standard_contract_type='ERC20',
        chain='testerchain',
        return_value_test=ReturnValueTest('==', 0),
        parameters=[
            ':userAddress',
        ]
    )
    return condition

@pytest.fixture
def sm_condition(test_registry):
    condition = ContractCondition(
        contract_address='0xadd9d957170DF6f33982001E4C22eCcDd5539118',
        method='getPolicy',
        chain='testerchain',
        function_abi=ABI,
        return_value_test=ReturnValueTest('!=', None),
        parameters=[
            ':hrac',
        ]
    )
    return condition


@pytest.fixture
def timelock_condition():
    condition = TimeCondition(
        return_value_test=ReturnValueTest('>', 0)
    )
    return condition


@pytest.fixture()
def lingo(timelock_condition, rpc_condition, evm_condition):
    lingo = ConditionLingo(
        conditions=[timelock_condition, OR, rpc_condition, AND, evm_condition]
    )
    return lingo