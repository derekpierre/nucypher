from enum import Enum
from typing import List, NamedTuple


class EthNetwork(Enum):
    MAINNET = 1
    GOERLI = 5
    SEPOLIA = 11155111
    # testing
    TESTERCHAIN = 131277322940537


class PolyNetwork(Enum):
    POLYGON = 137
    MUMBAI = 80001
    # testing
    TESTERCHAIN = 131277322940537


class TACoNetwork(NamedTuple):
    name: str
    eth_network: EthNetwork
    poly_network: PolyNetwork


class UnrecognizedNetwork(RuntimeError):
    """Raised when a provided network name is not recognized."""
    pass


class NetworksInventory:
    MAINNET = TACoNetwork("mainnet", EthNetwork.MAINNET, PolyNetwork.POLYGON)
    # Testnets
    ORYX = TACoNetwork("oryx", EthNetwork.GOERLI, PolyNetwork.POLYGON)
    LYNX = TACoNetwork("lynx", EthNetwork.GOERLI, PolyNetwork.MUMBAI)
    TAPIR = TACoNetwork("tapir", EthNetwork.SEPOLIA, PolyNetwork.MUMBAI)
    # TODO did Ibex even use a PolyNetwork?
    IBEX = TACoNetwork(
        "ibex", EthNetwork.GOERLI, PolyNetwork.MUMBAI
    )  # this is required for configuration file migrations (backwards compatibility)

    SUPPORTED_NETWORKS = [
        MAINNET,
        ORYX,
        LYNX,
        TAPIR,
        IBEX,
    ]

    SUPPORTED_NETWORK_NAMES = {network.name for network in SUPPORTED_NETWORKS}

    DEFAULT: str = MAINNET.name

    @classmethod
    def get_network(cls, network_name: str) -> TACoNetwork:
        for network in cls.SUPPORTED_NETWORKS:
            if network.name == network_name:
                return network

        raise UnrecognizedNetwork(f"{network_name} is not a recognized network.")

    @classmethod
    def get_network_names(cls) -> List[str]:
        networks = [network.name for network in cls.SUPPORTED_NETWORKS]
        return networks
