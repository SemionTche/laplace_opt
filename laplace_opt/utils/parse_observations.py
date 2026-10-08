'''
This file is made to parse the data received
from the server and extract the observations
required for the optimizer.
'''
# libraries
from laplace_log import log
import torch

# project
from ..core.optimizerContext import Observation
from ..model_construction import (
    InputStructure, ObjectiveStructure
)


def parse_results(results: list, 
                  inputs: dict[str, dict[str, str | int]], 
                  objective_list: list[ObjectiveStructure],
                  ) -> list[Observation]:
    '''
    Extract the data received from the server to make
    the observation tensors.
    '''
    observations = []
    n_obj = len(objective_list)

    for r in results:                          # for every results
        
        x_vals = []
        for name in inputs:                            # build x (the input position)
            info = inputs[name]
            addr = info["address"]
            pos = info["position_index"]
            x_vals.append(r["inputs"][addr][pos])

        x = torch.tensor(x_vals, dtype=torch.double)

        y_vals = torch.full(                            # build y (the objective values)
            (n_obj,),
            float("nan"),                               # ('nan' torch tensor)
            dtype=torch.double
        )

        outputs = r["outputs"]
        for i, obj in enumerate(objective_list):        # for each objective
            addr = obj.address
            key = obj.output_key

            if addr in outputs and key in outputs[addr]:
                y_vals[i] = outputs[addr][key]          # fill the torch tensor
        
        shot_number = r["shot_number_from_master"]

        observations.append(                            # add the observations
            Observation(
                x=x, 
                y=y_vals, 
                shot_number=shot_number
            )
        )  
    
    log.debug(
        f"Parsed {len(observations)} observations "
        f"(inputs_dim={observations[0].x.numel() if observations else 'n/a'}, "
        f"n_obj={n_obj})"
    )

    return observations