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
  
  def generate(self) -> List[Frame]:
    all_deployments_resources = sum([deployment.resources for deployment in self.config.deployments])
    edge_resources = sum([node.resources for node in self.config.nodes if node.is_on_edge])
    
    multiplications = edge_resources/all_deployments_resources
    multiplication = sum(multiplications)/len(multiplications)
    
    frames: List[Frame] = [Frame(replicas={}) for _ in range(self.config.number_of_cycles)]

    for deployment in self.config.deployments:
      shares = deployment.resources/all_deployments_resources
      share = sum(shares)/len(shares)
      
      coef = multiplication * share
      mean_replica = self.mean * coef
      sigma_replica = self.sigma * coef
      replicas = list(np.random.normal(mean_replica, sigma_replica, self.config.number_of_cycles))
      for i in range(len(replicas)):
        replicas[i] = max(replicas[i], 1)
        replicas[i] = round(replicas[i])

        frames[i].replicas[deployment] = replicas[i]

    return frames 
