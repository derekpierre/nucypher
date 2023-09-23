from typing import List, Optional, Dict

from ape.contracts.base import ContractInstance
from eth_utils import to_checksum_address

from nucypher.blockchain.eth.registry import InMemoryContractRegistry


def registry_from_ape_deployments(
    deployments: List[ContractInstance],
    registry_names: Optional[Dict[str, str]] = None,
) -> InMemoryContractRegistry:
    """Creates a registry from ape deployments."""
    registry_names = registry_names or dict()

    data = list()
    for contract_instance in deployments:
        abi_json_list = []
        for entry in contract_instance.contract_type.abi:
            abi_json_list.append(entry.dict())

        real_contract_name = contract_instance.contract_type.name
        contract_name = registry_names.get(
            real_contract_name,  # look up name in registry_names
            real_contract_name,  # default to the real contract name
        )

        entry = [
            contract_name,
            'v0.0.0',  # TODO: get version from contract
            to_checksum_address(contract_instance.address),
            abi_json_list,
        ]
        data.append(entry)
    registry = InMemoryContractRegistry()
    registry.write(data)
    return registry
