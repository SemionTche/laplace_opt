import torch

from .metric import Metric


class LOORMSE(Metric):

    name = "LOO RMSE"

    def compute(self, analyzer):

        mean, _, target = analyzer.loo_predictions()

        return torch.sqrt(
            ((mean - target) ** 2).mean()
        ).item()