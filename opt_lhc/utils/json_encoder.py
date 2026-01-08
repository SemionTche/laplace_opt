# libraries
import json
import inspect
import importlib


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