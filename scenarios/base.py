from typing import List

from data.scen import Frame
from data.base import Config

class Scenario:
  def __init__(self, command_args: List[str], config: Config):
    raise NotImplementedError
  
  def generate(self) -> List[Frame]:
    raise NotImplementedError
