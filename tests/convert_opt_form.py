# project
from laplace_opt.utils.getter import get_classes


def convert_opt_form(opt_form: dict) -> dict:
    '''
    Convert human-readable optimization form to optimizer-ready format
    with actual class objects instead of strings or dicts.
    '''
    new_opt_form = {}

    # ------------------
    # Execution panel
    # ------------------
    new_opt_form["exec"] = opt_form["exec"]

    # ------------------
    # Initialization
    # ------------------
    init_classes = get_classes("initializations")
    init_name, init_params = next(iter(opt_form["init"].items()))
    if init_name not in init_classes:
        raise ImportError(f"Cannot find initialization class {init_name}")
    new_opt_form["init"] = {
        "cls": init_classes[init_name],
        "params": {**init_params, "seed": 0}, # fix the seed for test repetability
    }

    # ------------------
    # Inputs
    # ------------------
    input_classes = get_classes("inputs")
    new_opt_form["inputs"] = {}
    for name in opt_form["inputs"]:
        if name not in input_classes:
            raise ImportError(f"Cannot find input class {name}")
        new_opt_form["inputs"][name] = input_classes[name](opt_form["inputs"][name]["bounds"])

    # ------------------
    # Objectives
    # ------------------
    obj_classes = get_classes("objectives")
    new_opt_form["obj"] = {}
    for name in opt_form["obj"]:
        if name not in obj_classes:
            raise ImportError(f"Cannot find objective class {name}")
        new_opt_form["obj"][name] = obj_classes[name](opt_form["obj"][name]["minimize"])

    # ------------------
    # Optimization pipeline
    # ------------------
    pipeline = opt_form.get("opt", {}).get("pipeline", {})
    is_opt = opt_form.get("opt", {}).get("enabled", False)
    
    if is_opt:
        # Acquisition
        acq_classes = get_classes("acquisitions")
        acq_name, acq_params = next(iter(pipeline.get("acquisition", {}).items()))
        if acq_name not in acq_classes:
            raise ImportError(f"Cannot find acquisition class {acq_name}")

        # Strategy
        strat_classes = get_classes("strategies")
        strat_name, strat_params = next(iter(pipeline.get("strategy", {}).items()))
        if strat_name not in strat_classes:
            raise ImportError(f"Cannot find strategy class {strat_name}")

        new_opt_form["opt"] = {
            "enabled": opt_form["opt"]["enabled"],
            "pipeline": {
                "acquisition": {"cls": acq_classes[acq_name], "params": acq_params},
                "strategy": {"cls": strat_classes[strat_name], "params": strat_params},
            },
        }
    else:
        new_opt_form["opt"] = {
            "enabled": opt_form["opt"]["enabled"],
            "pipeline": {}
        }

    return new_opt_form
