from typing import Dict, Any

from scenarios.base import Scenario

scenarios_dict: Dict[str, Scenario] = {}


def register_scenario(name: str):
    def wrapper(scenario):
        scenarios_dict[name] = scenario
        scenario.name = name
        return scenario

    return wrapper
