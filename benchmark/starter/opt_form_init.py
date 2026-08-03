OPT_FORM_INIT = {

    ### execution panel
    "exec": {
        "is_online": False,
        "is_reading_file": False,
        "reading_path": "",
        "saving_path": "",
        "server_address": ""
    },
    
    ### initialization
    "init": {
        "SobolInitialization": {
            "n_samples": 60,                 # the parameters
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
    },
    
    "opt": {
        "enabled": False,            # whether to optimize (True) or only initialize (False)
        
        "pipeline": {
            
            ### acquisition
            "acquisition": {
                "blank": ""
            },

            ### strategy
            "strategy": {
                "blank": ""
            }
        }
    },
}