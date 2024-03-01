import sys

from data.base import load_config
from data.scen import cycles_to_json

from scenarios.decorators import scenarios_dict

def main():
  if len(sys.argv) < 3:
    print("Usage: python genny.py <scenario_name> [<scenario_args>...]")
    return 1
  
  scenario_name = sys.argv[1]
  if scenario_name not in scenarios_dict:
    print(f"Scenario {scenario_name} not found.")
    return 1
  
  Scenario_cls = scenarios_dict[scenario_name]
  
  config = load_config("config.json")
  
  scenario = Scenario_cls(sys.argv[2:], config)
  frames = scenario.generate()

  with open("scen.json", "w") as f:
    f.write(cycles_to_json(frames, config))
  
  return 0

if __name__ == "__main__":
  sys.exit(main())
