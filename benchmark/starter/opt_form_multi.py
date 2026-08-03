OPT_FORM_MULTI = {
    
    ### execution panel
    "exec": {
        "is_online": False,
        "is_reading_file": False,
        "reading_path": "",
        "saving_path": "",
        "server_address": ""
    },

    ### criterium
    "criterium": {
        "max_iterations": 80,
        "n_repeats": 1,
        "save_period": 0,
        "is_optimization_criterium": False
    },

    ### initialization
    "init": {
        "SobolInitialization": {
            "n_samples": 4,                 # the parameters
            "q_candidates": 1,
            "seed": 0
        }
    },

    ### inputs
    "inputs": {
        "GasJetHeight": {
            "bounds": [-2.0, 10.0]
        },
        "GasJetLongitudinal": {
            "bounds": [-2.0, 9.0]
        },
    },
    
    ### objectives
    "obj": {
        "ElectronCharge": {
            "minimize": False
        },
        "ElectronEnergyMean": {
            "minimize": True
        },
    },
    
    "opt": {
        "enabled": True,            # whether to optimize (True) or only initialize (False)
        
        "pipeline": {
            
            ### acquisition
            "acquisition": {
                "qLogNEHVI": {
                    "alpha": 0.0,
                    "mc_samples": 128
                }
            },

            ### strategy
            "strategy": {
                "ModelList": {
                    # "n_repeats":5,
                    "num_restarts": 5,
                    "seed": 0,
                    "number_shot": 1,
                    "q_candidates": 1,
                    "raw_samples": 10,
                    "standardize_outputs": True
                }
            }
        }
    },
}