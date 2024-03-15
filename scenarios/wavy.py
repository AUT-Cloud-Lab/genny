import numpy as np

from typing import List, Dict

from data.scen import Frame
from data.base import Config, Deployment

from scenarios.base import Scenario
from scenarios.decorators import register_scenario

@register_scenario("wavy")
class WavyScenario(Scenario):
  def __init__(self, command_args: List[str], config: Config):
    try:
      # mean: base usage of edge usage (0: Minimum, 1: Maximum]
      self.base_usage = float(command_args[0])
      self.config = config
    except Exception as e:
      print("Could not parse the command arguments due to the following error:")
      print(str(e))
      
      raise Exception()
  
  def generate(self) -> List[Frame]:
    edge_resources = sum([node.resources for node in self.config.nodes if node.is_on_edge])
    all_resources = sum([node.resources for node in self.config.nodes])
    
    # INFO reducing couple of cores and gigabytes of memory for safety
    all_resources -= np.array([2, 2])

    frames: List[Frame] = [Frame(replicas={}) for _ in range(self.config.number_of_cycles)]

    base_state: Dict[Deployment, int] = {}
    for deployment in self.config.deployments:
      share = edge_resources * self.base_usage / len(self.config.deployments) / deployment.resources
      replica = sum(share)/len(share)
      base_state[deployment] = max(round(replica), 1)
    base_usage = sum([deployment.resources*replica for (deployment, replica) in base_state.items()])
    if (base_usage > all_resources).any():
      print("Base usage is greater than edge resources")
      raise Exception()

    for i in range(len(frames)):
      frames[i].replicas = {deployment: base_state[deployment] for deployment in self.config.deployments}

    cycles_start = 0
    for (deployment_ind, deployment) in enumerate(self.config.deployments):
      cycles_len = (self.config.number_of_cycles - cycles_start) // (len(self.config.deployments) - deployment_ind)
      cycle_end = cycles_start + cycles_len
      
      additional = 0
      while ((base_usage + additional * deployment.resources) <= all_resources).all():
        additional += 1
      additional -= 1

      assert additional >= 0

      raising_len = (cycles_len + 1) // 2
      falling_len = cycles_len - raising_len
      additional = min(additional, raising_len * 2)

      rasing_replicas = list(map(round,
        np.linspace(
          base_state[deployment], 
          base_state[deployment] + additional, 
          raising_len
        )
      ))
      failing_replicas = list(map(round,
        np.linspace(
          base_state[deployment] + additional,
          base_state[deployment], 
          falling_len + 1
        )
      ))
      failing_replicas.pop(0)
      replicas = rasing_replicas + failing_replicas
      
      assert len(replicas) == cycles_len
      
      for i in range(cycles_start, cycle_end):
        frames[i].replicas[deployment] = replicas[i - cycles_start]
      print(replicas)

      cycles_start = cycle_end

    return frames