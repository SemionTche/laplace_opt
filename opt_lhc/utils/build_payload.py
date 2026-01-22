# libraries
from collections import defaultdict
import torch


def get_inputs(input_opt: dict) -> tuple[dict[str, tuple], torch.Tensor]:
    '''
    Helper that extract the boundaries from the 'input_opt' dictionary
    stored in the optimization form.
    
    Return both a dictionary where the boundaries, input addresses
    and position_index are stored using there names and a 'Torch.Tensor' 
    to gather the boundaries in botorch format.
    '''
    bounds = []        # gather the boundaries
    inputs = {}        # information about the inputs
            
    for name, cls in input_opt.items():  # for each element
        bounds.append(cls.bounds)     # add the boundaries in the list
        # create the field to gather the address and the boundaries
        inputs[name] = {
            "address": cls.ip_port,
            "bounds": cls.bounds, 
            "position_index": cls.position_index
        }
    
    bounds = torch.Tensor(bounds).T   # convert the list to a tensor. The tensor must be 2 x d (d = input dimension)

    return inputs, bounds


def get_objectives(objective_opt) -> dict[str, list[str]]:
    '''
    Build objective specification grouped by address.

    Returns:
        {
            address: [output_key_1, output_key_2, ...]
        }
    '''
    obj_spec: dict[str, list[str]] = {}

    for obj in objective_opt.values():
        addr = obj.address
        key = obj.output_key

        obj_spec.setdefault(addr, []).append(key)

    return obj_spec


def build_data_payload(X: torch.Tensor, 
                       inputs: dict,
                       objectives,
                        *,
                        is_init: bool,
                        is_opt: bool) -> dict:
        '''
        Build the payload dictionary to be transmited through
        the server.

            Args:
                X: (torch.Tensor)
                    the sample candidates of shape (num_shot, n, q, d).
                
                inputs: (dict)
                    the input main informations: 
                        {name: {"bounds": ..., "address": ..., "position_index": ...}}
                    
                objectives: (dict)

                is_init: (bool)
                    indicating if it is the initialization suggested points.
                
                is_opt: (bool)
                    indicating if it is the optimization suggested points.
        '''
        payload = {}

        # making a dictionary of input addresses with the position size
        address_sizes = compute_address_sizes(inputs)

        # ensure CPU tensor for serialization
        X = X.cpu()

        samples = []

        for i in range(X.shape[0]):        # for each batch
            for j in range(X.shape[1]):    # for each candidate

                inp = {
                    addr: [None] * size
                    for addr, size in address_sizes.items()
                }                # NEW dict per sample

                for k, (name, info) in enumerate(inputs.items()):
                    addr = info["address"]
                    pos = info["position_index"]

                    inp[addr][pos] = X[i, j, k].item()

                # add the sample to the list
                samples.append({
                    "batch": i,
                    "candidate": j,
                    "inputs": inp,
                })

        payload = {
            "is_init": is_init,
            "is_opt": is_opt,
            "samples": samples,
            "obj": objectives
        }

        return payload



def compute_address_sizes(inputs: dict) -> dict[str, int]:
    '''
    Helper returning a dictionary indicating for each address
    the size of the position list.
    '''
    sizes = defaultdict(int)

    for info in inputs.values():
        addr = info["address"]
        pos = info["position_index"]
        sizes[addr] = max(sizes[addr], pos + 1)

    return dict(sizes)
