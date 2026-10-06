class CriteriumStructure:

    def __init__(self):

        self.parameters = {
            "max_iterations": {
                "type": int,
                "default": 2,
                "min": 0,
                "max": 10_000,
                "label": "Max iterations",
                "description": (
                    "Maximum number of model iterations (init + opt).\n"
                    "'0' meaning endless."
                )
            },

            "n_repeats": {
                "type": int,
                "default": 2,
                "min": 1,
                "max": 1000,
                "label": "Number sample repeats",
                "description": "Number of repeated evaluations per candidate."
            },

            "save_period": {
                "type": int,
                "default": 1,
                "min": 0,
                "max": 100,
                "label": "Saving period",
                "description": (
                    "Number of optimization steps between automatic saves.\n"
                    "Set to '0' to disable."
                )
            },
        }