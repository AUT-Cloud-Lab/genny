import json
import numpy as np
from typing import Tuple, Dict, List, Any
from dataclasses import dataclass

from data.base import Deployment, Config

@dataclass
class Frame:
    replicas: Dict[Deployment, int]

    def evaluate(self, config: Config) -> np.ndarray:
        resource_shape = config.nodes[0].resources.shape
        resource_requested = np.zeros(resource_shape)
        for deployment, replica in self.replicas.items():
            if replica <= 0:
                raise ValueError(f"Replica count of {deployment.name} is {replica}, which is invalid.")
            resource_requested += replica * deployment.resources
        
        if any(resource_requested > sum([node.resources for node in config.nodes])):
            raise ValueError("Resource usage exceeds the total capacity.")
        
        return resource_requested


def cycles_to_json(frames: List[Frame], config: Config) -> str:
    frames_resource_requested = [frame.evaluate(config) for frame in frames]
    
    with open("resource_requested.csv", "w") as f:
        f.write("CPU(cores),Memory(GB)\n")
        for resource_requested in frames_resource_requested:
            f.write(f"{resource_requested[0]},{resource_requested[1]}\n")

    apis: List[Dict[str, Any]] = []

    for deployment in config.deployments:
        api: Dict[str, Any] = {}
        api["name"] = deployment.name
        api["endpoint"] = deployment.endpoint
        
        intervals: List[Dict[str, Any]] = []
        def get_interval(replica, cnt):
            interval = {}

            period = 1000 / (replica * config.threshold)
            length = cnt * config.cycle_length
            interval["api_call_period"] = period
            interval["cycle_length"] = length

            return interval
        
        cnt = 1
        last_replica = frames[0].replicas[deployment]
        for i in range(1, len(frames)):
            if last_replica == frames[i].replicas[deployment]:
                cnt += 1
                continue
            
            intervals.append(get_interval(last_replica, cnt))
            
            last_replica = frames[i].replicas[deployment]
            cnt = 1
        
        intervals.append(get_interval(last_replica, cnt))
        api["intervals"] = intervals
        apis.append(api)
    
    return json.dumps({"apis": apis})
