import json
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

    cycle_length: int  # ms
    number_of_cycles: int
    threshold: int  # rate limit threshold of the HPA


def load_config(path: str) -> Config:
    with open(path, "r") as f:
        data = json.load(f)

    deployments = [
        Deployment(
            deployment["name"],
            deployment["endpoint"],
            np.array(deployment["resources"]),
        )
        for deployment in data["deployments"]
    ]

    nodes = [
        Node(
            data["name"],
            # Removing 1 core, and 1 GB of memory from each node's resources
            np.array(list(map(lambda r: r-1, data["resources"]))), 
            data["is_on_edge"]
        )
        for data in data["nodes"]
    ]

    return Config(
        deployments,
        nodes,
        data["cycle_length"],
        data["number_of_cycles"],
        data["threshold"],
    )
