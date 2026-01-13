import torch
from botorch.utils.transforms import normalize

class OptimizationContext:
    def __init__(self, train_X_list, train_Y_list, bounds, objectives):
        self.train_X_list = train_X_list
        self.train_Y_list = train_Y_list
        self.bounds = bounds
        self.objectives = objectives
    
    def get_X_baseline(self) -> torch.Tensor:
        """
        Return the union of all evaluated design points,
        suitable for NEHVI / LogNEHVI.
        """
        Xs = []

        for X in self.train_X_list:
            if isinstance(X, torch.Tensor) and X.numel() > 0:
                Xs.append(X)

        if len(Xs) == 0:
            raise RuntimeError("No baseline points available.")

        # concatenate and drop duplicates
        X_all = torch.cat(Xs, dim=0)
        X_unique = torch.unique(X_all, dim=0)

        return X_unique
    
    def get_X_baseline_normalized(self) -> torch.Tensor:
        return normalize(self.get_X_baseline(), self.bounds)
    

    def compute_ref_point(self) -> torch.Tensor:
        ref = []
        for i, obj in enumerate(self.objectives.values()):
            y = self.train_Y_list[i].squeeze(-1)

            if obj.minimize:
                ref.append(y.max() + 0.1 * y.abs().max())
            else:
                ref.append(y.min() - 0.1 * y.abs().max())

        return torch.tensor(ref, dtype=torch.double)
