import torch

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from laplace_opt.core.optimizer import Optimizer

from tests.convert_opt_form import convert_opt_form
from tests.optimization.single_objective_process import run_single_objective
from tests.optimization.multi_objective_process import run_multi_objective


# ==========================
# USER CONFIGURATION
# ==========================
TEST_MODE = "multi"      # "single" or "multi"


OPT_FORM = {
    "init": {
        "SobolInitialization": {
            "n_samples": 3,
            "q_candidates": 2,
        }
    },
    
    "inputs": {
        "GasJetHeight": {"bounds": [0.0, 10.0]},
        "GasJetLongitudinal": {"bounds": [0.0, 10.0]},
    },
    
    "obj": {
        "ElectronCharge": {"minimize": False},
        "ElectronEnergyMean": {"minimize": False},
    },
    
    "opt": {
        "enabled": True,
        "pipeline": {
            "acquisition": {
                "qLogNEHVI": {
                    "alpha": 0.0,
                    "mc_samples": 128
                }
            },
            "strategy": {
                "ModelList": {
                    "num_restarts": 5,
                    "number_shot": 1,
                    "q_candidates": 2,
                    "raw_samples": 10,
                    "standardize_outputs": True
                }
            }
        }
    },
}



if __name__ == "__main__":
    torch.manual_seed(0)

    OPT_FORM = convert_opt_form(OPT_FORM)
    print(OPT_FORM)

    optimizer = Optimizer(OPT_FORM)
    optimizer.init_opt()

    if TEST_MODE == "single":
        run_single_objective(optimizer)
    elif TEST_MODE == "multi":
        run_multi_objective(optimizer)
    else:
        raise ValueError(f"Unknown TEST_MODE: {TEST_MODE}")
