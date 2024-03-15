import os
import pathlib

from typing import List, Tuple

from data.scen import Frame
from data.base import Config


class Scenario:
    def __init__(self, command_args: List[str], config: Config):
        raise NotImplementedError

    def get_properties(self) -> str:
        raise NotImplementedError

    def get_out_paths(self) -> Tuple[str, str]:
        if not os.path.exists("out"):
            print(
                f"""
            No out direction found or multiple out directories found.
            Path: {os.getcwd()}
            """
            )

        base_dir = "out"
        base_dir = os.path.join(base_dir, self.name)
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)

        f_name = "_".join(map(str, self.get_properties()))
        return (
            os.path.join(base_dir, f"scenario_{f_name}.json"),
            os.path.join(base_dir, f"resource_{f_name}.csv"),
        )

    def generate(self) -> List[Frame]:
        raise NotImplementedError
