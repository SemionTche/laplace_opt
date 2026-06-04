import torch


class PostAnalysis():

    def __init__(self):
        pass

    def load(self, path: str) -> None:
        self.data = torch.load(path, weights_only=False)
        self.extract_data()


    def extract_data(self) -> None:
        '''
        Function made to extract all the relevant features from
        the data attribute.
        '''

        # main entries
        self.meta = self.data["metadata"]
        self.problem = self.data["problem"]
        self.observations = self.data["observations"]
        self.model = self.data["model"]
        self.acquisition = self.data["acquisition"]
        self.best_results_saved = self.data["best_results"]
        self.suggestions_saved = self.data["suggestions"]
        self.rng_state = self.data["rng_state"]

        # from the metadata
        self.saving_data = self.meta["saving_data"]
        self.saving_time = self.meta["saving_time"]
        self.start_day = self.meta["start_day"]
        self.start_time = self.meta["start_time"]

        self.n_inputs = self.meta["n_inputs"]
        self.n_init = self.meta["n_init"]       # position and repeats
        self.optimization_step = self.meta["optimization_step"]
        self.init_and_opt_step = self.meta["init_and_opt_step"]
        self.criterium = self.meta["criterium"]

        # from the problem
        self.bounds = self.problem["bounds"]
        self.inputs = self.problem["inputs"]
        self.objectives = self.problem["objectives"]
        self.init = self.problem["init"]
        self.strategy = self.problem["strategy"]
        self.acquisition = self.problem["acquisition"]
        self.opt_form = self.problem["opt_form"]

        # from observations
        self.X_physical = self.observations["X_physical"]
        self.Y_physical = self.observations["Y_physical"]
        self.X_norm = self.observations["X_norm"]
        self.Y_opt_space = self.observations["Y_opt_space"]
        self.shot_numbers = self.observations["shot_numbers"]

        self.model_cls = self.model["model_class"]
        self.model_state_dict = self.model["model_state_dict"]
        
        self.acquisition_cls = self.acquisition["acquisition_class"]
        self.acquisition_state_dict = self.acquisition["acquisition_state_dict"]

