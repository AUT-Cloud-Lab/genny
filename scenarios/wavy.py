import os
from typing import List, Dict, Tuple

import numpy as np

from data.base import Config, Deployment
from data.scen import Frame
from scenarios.base import Scenario
from scenarios.decorators import register_scenario


@register_scenario("wavy")
class WavyScenario(Scenario):
    def __init__(self, command_args: List[str], config: Config):
        try:
            # mean: base usage of edge usage (0: Minimum, 1: Maximum]
            self.base_usage = float(command_args[0])
            self.number_of_deployments = int(command_args[1])
            self.config = config
        except Exception as e:
            print("Could not parse the command arguments due to the following error:")
            print(str(e))

            raise Exception()

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
        self.ensure_directory(base_dir)

        f_name = "_".join(map(str, self.get_properties()))
        return (
            os.path.join(base_dir, f"wavy_scenario_{f_name}.json"),
            os.path.join(base_dir, f"wavy_resource_{f_name}.csv"),
        )

    def get_properties(self) -> str:
        return [self.base_usage, self.number_of_deployments]

    def generate(self) -> List[Frame]:
        edge_resources = sum(
            [node.resources for node in self.config.nodes if node.is_on_edge]
        )
        all_resources = sum([node.resources for node in self.config.nodes])

        # INFO reducing a couple of cores and gigabytes of memory for safety
        all_resources -= np.array([2, 2])

        frames: List[Frame] = [
            Frame(replicas={}) for _ in range(self.config.number_of_cycles)
        ]

        base_state: Dict[Deployment, int] = {}
        for deployment in self.config.deployments:
            share = (
                    edge_resources
                    * self.base_usage
                    / len(self.config.deployments)
                    / deployment.resources
            )
            replica = sum(share) / len(share)
            base_state[deployment] = max(round(replica), 1)
        base_usage = sum(
            [
                deployment.resources * replica
                for (deployment, replica) in base_state.items()
            ]
        )
        if (base_usage > all_resources).any():
            print("Base usage is greater than edge resources")
            raise Exception()

        for i in range(len(frames)):
            frames[i].replicas = {
                deployment: base_state[deployment]
                for deployment in self.config.deployments
            }

        cycles_start = 0
        for (deployment_ind, deployment) in enumerate(
                self.config.deployments[: self.number_of_deployments]
        ):
            cycles_len = (self.config.number_of_cycles - cycles_start) // (
                    self.number_of_deployments - deployment_ind
            )
            cycle_end = cycles_start + cycles_len

            additional = 0
            while (
                    (base_usage + additional * deployment.resources) <= all_resources
            ).all():
                additional += 1
            additional -= 1

            assert additional >= 0

            raising_len = (cycles_len + 1) // 2
            falling_len = cycles_len - raising_len
            additional = min(additional, (raising_len - 1) * 3)

            rasing_replicas = list(
                map(
                    round,
                    np.linspace(
                        base_state[deployment],
                        base_state[deployment] + additional,
                        raising_len,
                    ),
                )
            )
            failing_replicas = list(
                map(
                    round,
                    np.linspace(
                        base_state[deployment] + additional,
                        base_state[deployment],
                        falling_len + 1,
                    ),
                )
            )
            failing_replicas.pop(0)
            replicas = rasing_replicas + failing_replicas

            assert len(replicas) == cycles_len

            for i in range(cycles_start, cycle_end):
                frames[i].replicas[deployment] = replicas[i - cycles_start]
            print(replicas)

            cycles_start = cycle_end

        return frames
