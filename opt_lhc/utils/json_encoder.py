# libraries
import json
import inspect
import importlib
import torch


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


def json_style(d: dict) -> str:
    '''Return a JSON string of a dictionary for logging.'''
    try:
        return json.dumps(d, indent=4, sort_keys=True, default=str)
    except Exception as e:
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