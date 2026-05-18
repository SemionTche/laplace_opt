# libraries
import json
import inspect
import importlib
import torch

from laplace_log import log


def print_batch(X: torch.Tensor, inputs: dict) -> str:
    '''
    Print the values that each input should take. Use a X 'torch.Tensor'
    for the values and a 'inputs' dictionary for the input addresses.
    '''
    addresses = [v["address"] for v in inputs.values()]  # make a list of addresses
    position_index = [v["position_index"] for v in inputs.values()]

    lines = []
    for i in range(X.shape[0]):                            # for each sample
        lines.append(f"batch {i + 1}:")                     # print which sample it is
        for j in range(X.shape[1]):                          # for each candidate
            coords = ", ".join(
                f"{addr}|{pos}={X[i, j, k].item():.6g}"            # for each input, address = value
                for k, (addr, pos) in enumerate(zip(addresses, position_index))
            )
            lines.append(f"  Candidate {j + 1}: {coords}")   # print the candidate
    
    return "\n".join(lines)


def format_candidate_batch(X: torch.Tensor, 
                           inputs: dict,
                           *,
                           precision: int = 6,) -> str:
    '''
    Pretty-print candidate batches using semantic input names.

    X shape: (n_batches, n_candidates, n_inputs)
    inputs: dict[name -> metadata]
    '''
    input_names = list(inputs.keys())
    fmt = f"{{:.{precision}g}}"

    lines: list[str] = []

    for i in range(X.shape[0]):  # batch
        lines.append(f"batch {i + 1}:")
        for j in range(X.shape[1]):  # candidate
            lines.append(f"  Candidate {j + 1}:")
            lines.append("    Inputs:")
            for k, name in enumerate(input_names):
                value = fmt.format(X[i, j, k].item())
                lines.append(f"      {name} = {value}")

    return "\n".join(lines)


def print_evaluations(data: list[dict], inputs: dict,) -> str:
    '''
    Pretty-print evaluated inputs and objectives from server OPT messages.
    '''
    print(f"we want to print data = {data}, inputs = {inputs}")
    # Map position_index to input name
    index_to_name = {
        v["position_index"]: name
        for name, v in inputs.items()
    }

    lines = []     # list of lines to print

    # Sort for deterministic output
    data = sorted(data, key=lambda d: (d["batch"], d["candidate"], d["shot_number_from_master"]))

    current_batch = None

    for item in data:                                           # for element in the data
        batch = item["batch"]                                   # get the batch
        candidate = item["candidate"]                           # get the candidate
        shot_number = item["shot_number_from_master"]                       # get the shot number
        
        if batch != current_batch:                              # if it is not the current batch
            lines.append(f"batch {batch + 1}:")                 # print the batch number
            current_batch = batch                               # set the current batch

        lines.append(f"  Candidate {candidate + 1} (shot_number {shot_number}):")           # print the candidate

        # Inputs
        lines.append("    Inputs:")
        for addr, values in item["inputs"].items():             # for each input
            # print(f"values are = {values}, type = {type(values)}")
            for i, value in enumerate(values):    
                # print(f"value is = {value}, type = {type(value)}, i = {i}")              # for each value
                if value is None:
                    continue
                name = index_to_name.get(i, f"input_{i}")       # get the input name
                lines.append(f"      {name} = {value:.6g}")     # print name = value

        # Outputs
        lines.append("    Objectives:")
        for _, obj_dict in item["outputs"].items():             # for each objective
            for obj_name, value in obj_dict.items():           # for each value
                # usually one value per evaluation
                print(f"values obj = {value}, type = {type(value)}, obj name = {obj_name}")
                print(f"obj dict = {obj_dict}")
                val = value if value else None
                lines.append(f"      {obj_name} = {val:.6g}")   # print name = value

    return "\n".join(lines)                                     # return the lines to print



def json_style(d: dict, json_cls=None) -> str:
    '''Return a JSON string of a dictionary.'''
    try:
        return json.dumps(d, indent=4, sort_keys=True, default=str, cls=json_cls)
    except Exception as e:
        log.error(f"Error: {e}\nGoing back for string config.")
        return str(d)  # fallback if object is not JSON serializable


class OptimizationJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Classes
        if inspect.isclass(obj):
            return {
                "__type__": "class",
                "module": obj.__module__,
                "name": obj.__qualname__,
            }

        # Class instances
        if hasattr(obj, "__class__"):
            return {
                "__type__": "instance",
                "class": f"{obj.__class__.__module__}.{obj.__class__.__qualname__}",
                "repr": repr(obj),
            }

        return super().default(obj)


def load_class(path: str):
    module, name = path.rsplit(".", 1)
    return getattr(importlib.import_module(module), name)