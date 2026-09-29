import torch

from .base import TestFunction


class ReverseFunction:

    def __init__(self, function: TestFunction):

        self.function = function

        self.name = function.name + "_reversed"

        self.bounds = function.bounds

        self.n_inputs = function.n_inputs

        self.n_objectives = function.n_objectives

        self.minimize = not function.minimize

        self.mode = function.mode


    def __call__(self, *x):

        return - self.function(*x)