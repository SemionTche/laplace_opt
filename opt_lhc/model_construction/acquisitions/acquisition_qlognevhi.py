from model_construction.acquisitions.acquisition_structure import AcquisitionStructure

class qLogNEHVI(AcquisitionStructure):
    display_name = "qLogNEHVI"
    parameters = {
        "mc_samples": {"type": int, "default": 128}
    }

    def build(self, model, sampler, mc_samples=128):
        from botorch.acquisition.multi_objective.logei import (
            qLogNoisyExpectedHypervolumeImprovement
        )

        return qLogNoisyExpectedHypervolumeImprovement(
            model=model,
            sampler=sampler
        )
