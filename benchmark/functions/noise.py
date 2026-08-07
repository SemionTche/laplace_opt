import torch

from .base import TestFunction


class NoisyFunction:

    def __init__(self, function: TestFunction, relative_noise=0.05):

        self.function = function

        self.relative_noise = relative_noise

        self.name = function.name + "_noisy"

        self.bounds = function.bounds

        self.optimum_input = function.optimum_input

        self.optimum_obj = function.optimum_obj

        self.n_inputs = function.n_inputs

        self.n_objectives = function.n_objectives

        self.mode = function.mode


    def __call__(self, *x):

        y = self.function(*x)

        eps = self.relative_noise * torch.abs(y)

        y += eps * (2 * torch.rand_like(y) - 1)

        return y