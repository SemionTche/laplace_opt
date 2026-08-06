import torch
from torch.distributions import Normal

from .metric import Metric


class LOONLPD(Metric):

    name = "LOO NLPD"

    def compute(self, analyzer):

        mean, var, target = analyzer.loo_predictions()

        std = torch.sqrt(
            torch.clamp(
                var,
                min=1e-12,
            )
        )

        dist = Normal(mean, std)

        return (
            -dist.log_prob(target)
            .mean()
            .item()
        )