# libraries
import json
import inspect
import importlib


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