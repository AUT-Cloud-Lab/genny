import numpy as np
from typing import Tuple, List
from dataclasses import dataclass

@dataclass
class Deployment:
    name: str
    endpoint: str
    resources: np.ndarray

    def __hash__(self) -> int:
        return hash(self.name)

@dataclass
class Node:
    name: str
    resources: np.ndarray
    is_on_edge: bool

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Config:
    deployments: List[Deployment]
    nodes: List[Node]
    
    cycle_length: int # ms
    number_of_cycles: int
    threshold: int # rate limit threshold of the HPA
