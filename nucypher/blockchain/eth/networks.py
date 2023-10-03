from enum import Enum
from typing import NamedTuple

from nucypher.config.constants import TEMPORARY_DOMAIN


class ChainInfo(NamedTuple):
    id: int
    name: str


class EthChain(ChainInfo, Enum):
    MAINNET = ChainInfo(1, "mainnet")
    GOERLI = ChainInfo(5, "goerli")
    SEPOLIA = ChainInfo(11155111, "sepolia")
    TESTERCHAIN = ChainInfo(131277322940537, TEMPORARY_DOMAIN)


class PolygonChain(ChainInfo, Enum):
    POLYGON = ChainInfo(137, "polygon")
    MUMBAI = ChainInfo(80001, "mumbai")
    TESTERCHAIN = ChainInfo(131277322940537, TEMPORARY_DOMAIN)


class TACoDomain(NamedTuple):
    name: str
    eth_chain: EthChain
    polygon_chain: PolygonChain

    def is_testnet(self) -> bool:
        return self.eth_chain != EthChain.MAINNET


class UnrecognizedDomain(RuntimeError):
    """Raised when a provided domain name is not recognized."""


class NetworksInventory:
    MAINNET = TACoDomain("mainnet", EthChain.MAINNET, PolygonChain.POLYGON)
    # Testnets
    ORYX = TACoDomain("oryx", EthChain.GOERLI, PolygonChain.POLYGON)
    LYNX = TACoDomain("lynx", EthChain.GOERLI, PolygonChain.MUMBAI)
    TAPIR = TACoDomain("tapir", EthChain.SEPOLIA, PolygonChain.MUMBAI)
    # TODO did Ibex even use a PolyNetwork?
    IBEX = TACoDomain(
        "ibex", EthChain.GOERLI, PolygonChain.MUMBAI
    )  # this is required for configuration file migrations (backwards compatibility)

    SUPPORTED_DOMAINS = [
        MAINNET,
        ORYX,
        LYNX,
        TAPIR,
        IBEX,
    ]

    SUPPORTED_DOMAIN_NAMES = [network.name for network in SUPPORTED_DOMAINS]

    # TODO not needed once merged with registry changes
    POLYGON_CHAINS = [network.polygon_chain.name for network in SUPPORTED_DOMAINS]

    DEFAULT_DOMAIN_NAME: str = MAINNET.name

    @classmethod
    def from_domain_name(cls, domain: str) -> TACoDomain:
        for taco_domain in cls.SUPPORTED_DOMAINS:
            if taco_domain.name == domain:
                return taco_domain

        raise UnrecognizedDomain(f"{domain} is not a recognized domain.")
