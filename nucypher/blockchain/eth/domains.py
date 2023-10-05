from enum import Enum
from typing import NamedTuple


class ChainInfo(NamedTuple):
    id: int
    name: str


class EthChain(ChainInfo, Enum):
    MAINNET = (1, "mainnet")
    GOERLI = (5, "goerli")
    SEPOLIA = (11155111, "sepolia")
    TESTERCHAIN = (131277322940537, "eth-tester")


class PolygonChain(ChainInfo, Enum):
    POLYGON = (137, "polygon")
    MUMBAI = (80001, "mumbai")
    TESTERCHAIN = (131277322940537, "eth-tester")


class TACoDomain(NamedTuple):
    name: str
    eth_chain: EthChain
    polygon_chain: PolygonChain

    @property
    def is_testnet(self) -> bool:
        return self.eth_chain != EthChain.MAINNET


class TACoDomains:
    class Unrecognized(RuntimeError):
        """Raised when a provided domain name is not recognized."""

    MAINNET = TACoDomain("mainnet", EthChain.MAINNET, PolygonChain.POLYGON)
    # Testnets
    ORYX = TACoDomain("oryx", EthChain.GOERLI, PolygonChain.POLYGON)
    LYNX = TACoDomain("lynx", EthChain.GOERLI, PolygonChain.MUMBAI)
    TAPIR = TACoDomain("tapir", EthChain.SEPOLIA, PolygonChain.MUMBAI)
    IBEX = TACoDomain(
        "ibex", EthChain.GOERLI, None
    )  # this is required for configuration file migrations (backwards compatibility)

    DEFAULT_DOMAIN_NAME: str = MAINNET.name

    SUPPORTED_DOMAINS = [
        MAINNET,
        ORYX,
        LYNX,
        TAPIR,
    ]

    SUPPORTED_DOMAIN_NAMES = [domain.name for domain in SUPPORTED_DOMAINS]

    @classmethod
    def from_domain_name(cls, domain: str) -> TACoDomain:
        for taco_domain in cls.SUPPORTED_DOMAINS:
            if taco_domain.name == domain:
                return taco_domain

        raise cls.Unrecognized(f"{domain} is not a recognized domain.")
