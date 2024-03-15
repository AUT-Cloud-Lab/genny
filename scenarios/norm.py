import numpy as np

from typing import List

from data.scen import Frame
from data.base import Config

from scenarios.base import Scenario
from scenarios.decorators import register_scenario

@register_scenario("normal")
class NormalScenario(Scenario):
  def __init__(self, command_args: List[str], config: Config):
    try:
      # mean: Average of edge usage (0: Minimum, 1: Maximum]
      self.mean = float(command_args[0])
      self.sigma = float(command_args[1])
      self.config = config
    except Exception as e:
      print("Could not parse the command arguments due to the following error:")
      print(str(e))
      
      raise Exception()
  
  def get_properties(self) -> str:
    return [self.mean, self.sigma]

  def generate(self) -> List[Frame]:
    edge_resources = sum([node.resources for node in self.config.nodes if node.is_on_edge])
        
    frames: List[Frame] = [Frame(replicas={}) for _ in range(self.config.number_of_cycles)]

    for deployment in self.config.deployments:
      share = edge_resources / len(self.config.deployments) / deployment.resources
      coef = sum(share)/len(share)
      
      mean_replica = self.mean * coef
      sigma_replica = self.sigma * coef
      replicas = list(np.random.normal(mean_replica, sigma_replica, self.config.number_of_cycles))
      print(f"{coef}")
      for i in range(len(replicas)):
        replicas[i] = round(replicas[i])
        replicas[i] = max(replicas[i], 1)

        frames[i].replicas[deployment] = replicas[i]
      print(replicas)

    return frames 
