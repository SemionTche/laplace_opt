from .base import TestFunction
from .sphere import Sphere
from .booth import Booth
from .beale import Beale
from .himmelblau import Himmelblau
from .rosenbrock import Rosenbrock
from .branin_hoo import BraninHoo
from .ackley import Ackley
from .rastrigin import Rastrigin
from .goldstein_price import GoldsteinPrice
from .styblinski_tang import StyblinskiTang

from .noise import NoisyFunction
from .reverse import ReverseFunction


FUNCTIONS: dict[str, type[TestFunction]] = {
    "Sphere": Sphere,
    "Booth": Booth,
    "Beale": Beale,
    "Himmelblau": Himmelblau,
    "Rosenbrock": Rosenbrock,
    "Branin": BraninHoo,
    "Ackley": Ackley,
    "Rastrigin": Rastrigin,
    "GoldsteinPrice": GoldsteinPrice,
    "StyblinskiTang": StyblinskiTang,
}