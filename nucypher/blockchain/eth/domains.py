from enum import Enum
from typing import NamedTuple, Dict


class UnrecognizedTacoDomain(Exception):
    """Raised when a domain is not recognized."""


class ChainInfo(NamedTuple):
    id: int
    name: str


class EthChain(ChainInfo, Enum):
    MAINNET = (1, "mainnet")
    GOERLI = (5, "goerli")
    SEPOLIA = (11155111, "sepolia")


class PolygonChain(ChainInfo, Enum):
    MAINNET = (137, "polygon")
    MUMBAI = (80001, "mumbai")


class TACoDomain:

    def __init__(self,
                 name: str,
                 eth_chain: EthChain,
                 polygon_chain: PolygonChain,
                 ):
        self.name = name
        self.eth_chain = eth_chain
        self.polygon_chain = polygon_chain

    def __repr__(self):
        return f"<TACoDomain {self.name}>"

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __bytes__(self):
        return self.name.encode()

    def __eq__(self, other):
        try:
            return self.name == other.name
        except AttributeError:
            raise TypeError(f"Cannot compare TACoDomain to {type(other)}")

    def __bool__(self):
        return True

    def __iter__(self):
        return str(self)

    @property
    def is_testnet(self) -> bool:
        return self.eth_chain != EthChain.MAINNET


MAINNET = TACoDomain(
    name="mainnet",
    eth_chain=EthChain.MAINNET,
    polygon_chain=PolygonChain.MAINNET,
)

LYNX = TACoDomain(
    name="lynx",
    eth_chain=EthChain.GOERLI,
    polygon_chain=PolygonChain.MUMBAI,
)

TAPIR = TACoDomain(
    name="tapir",
    eth_chain=EthChain.SEPOLIA,
    polygon_chain=PolygonChain.MUMBAI,
)

__DOMAINS = (MAINNET, LYNX, TAPIR)

DEFAULT_DOMAIN: TACoDomain = MAINNET

SUPPORTED_DOMAINS: Dict[str, TACoDomain] = {domain.name: domain for domain in __DOMAINS}



def get_domain(d: str) -> TACoDomain:
    if not isinstance(d, str):
        raise TypeError(f"domain must be a string, not {type(d)}")
    for name, domain in SUPPORTED_DOMAINS.items():
        if name == d == domain.name:
            return domain
    raise UnrecognizedTacoDomain(f"{d} is not a recognized domain.")
