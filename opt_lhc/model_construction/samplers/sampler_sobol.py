from model_construction.samplers.sampler_structure import SamplerStructure

class SobolSampler(SamplerStructure):
    display_name = "Sobol QMC"
    parameters = {
        "num_samples": {"type": int, "default": 128}
    }

    def build(self, num_samples=128):
        from botorch.sampling import SobolQMCNormalSampler
        return SobolQMCNormalSampler(sample_shape=(num_samples,))
