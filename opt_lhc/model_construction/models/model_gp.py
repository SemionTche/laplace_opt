from model_construction.models.model_structure import ModelStructure

class GaussianGP(ModelStructure):
    display_name = "Gaussian Process"
    parameters = {
        "noise": {"type": float, "default": 1e-6}
    }

    def build(self, train_X, train_Y, noise=1e-6):
        import torch
        from botorch.models import SingleTaskGP
        from gpytorch.likelihoods import GaussianLikelihood

        likelihood = GaussianLikelihood(noise_constraint=None)
        likelihood.noise = noise

        return SingleTaskGP(train_X, train_Y, likelihood=likelihood)
