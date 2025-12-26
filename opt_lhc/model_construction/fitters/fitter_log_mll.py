from model_construction.fitters.fitter_structure import FitterStructure

class LogMarginalLikelihood(FitterStructure):
    display_name = "Log Marginal Likelihood"
    parameters = {}

    def fit(self, model):
        from botorch.fit import fit_gpytorch_mll
        from gpytorch.mlls import ExactMarginalLogLikelihood

        mll = ExactMarginalLogLikelihood(model.likelihood, model)
        fit_gpytorch_mll(mll)
        return model
