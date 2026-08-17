from .metric import Metric


from .regret import (
    SimpleRegret, AreaUnderRegretCurve, CumulativeRegret
)
from .time_to_epsilon import TimeToEpsilon
from .distance_to_optimum import DistanceToOptimum

from .loo_rmse import LOORMSE
from .loo_nlpd import LOONLPD
from .coverage import Coverage

from .contractions import (
    FinalVarianceContraction,
    FinalEntropyContraction,
    HalfLifeVarianceContraction,
    HalfLifeEntropyContraction,
)

from .lengthscale_stats import LengthscaleMean, LengthscaleStd
from .noise_stats import NoiseMean, NoiseStd


METRICS: dict[str, Metric] = {
    "SimpleRegret": SimpleRegret(),
    # "CumulativeRegret": CumulativeRegret(),
    "AreaUnderRegretCurve": AreaUnderRegretCurve(),
    "TimeToEpsilon": TimeToEpsilon(),
    # "DistanceToOptimum": DistanceToOptimum(),

    # "LOORMSE": LOORMSE(),
    # "LOONLPD": LOONLPD(),
    # "Covarage": Coverage(),

    "FinalVarianceContraction": FinalVarianceContraction(),
    "FinalEntropyContraction": FinalEntropyContraction(),

    "HalfLifeVarianceContraction": HalfLifeVarianceContraction(),
    "HalfLifeEntropyContraction": HalfLifeEntropyContraction(),

    # "LengthscaleMean": LengthscaleMean(),
    # "LengthscaleStd": LengthscaleStd(),
    # "NoiseMean": NoiseMean(),
    # "NoiseStd": NoiseStd(),
}