# libraries
from dataclasses import dataclass

import torch

# project
from laplace_opt.core.optimizerContext import OptimizationContext


@dataclass
class RunMetadata:
    saving_date: str
    saving_time: str

    n_inputs: int
    n_objs: int
    n_observations: int

    n_init: int
    n_repeats: int

    optimization_step: int
    init_and_opt_step: int

@dataclass
class Objective:
    name: str
    minimize: bool

class PostAnalysis:

    def __init__(self, path: str | None = None):
        # self.data = None

        # self.metadata = None
        # self.problem = None
        # self.observations = None

        if path is not None:
            self.load(path)


    def load(self, path: str) -> None:

        self.data = torch.load(path, weights_only=False)

        self.metadata = self.data["metadata"]
        self.problem = self.data["problem"]
        self.observations = self.data["observations"]

        self._extract_metadata()


    def _extract_metadata(self):

        meta = self.metadata

        self.info = RunMetadata(
            saving_date=meta["saving_date"],
            saving_time=meta["saving_time"],
            n_inputs=meta["n_inputs"],
            n_objs=self.observations["Y_physical"].shape[-1],
            n_observations=meta["n_observations"],
            n_init=meta["n_init"],
            n_repeats=meta["criterium"]["n_repeats"],
            optimization_step=meta["optimization_step"],
            init_and_opt_step=meta["init_and_opt_step"],
        )
        self.summary()

    @property
    def X_physical(self):
        return self.observations["X_physical"]

    @property
    def Y_physical(self):
        return self.observations["Y_physical"]

    @property
    def X_normalized(self):
        return self.observations["X_normalized"]

    @property
    def Y_opt_space(self):
        return self.observations["Y_opt_space"]
    
    @property
    def X_optimization(self):
        return self.X_physical[self.info.n_init:]

    @property
    def shot_numbers(self):
        return self.observations["shot_numbers"]


    def summary(self) -> None:
        print(
            f"""
            Date: {self.info.saving_date} {self.info.saving_time}
            Observations: {self.info.n_observations}
            Inputs: {self.info.n_inputs}
            Objectives: {self.info.n_objs}
            Initial observations: {self.info.n_init}
            Repeats: {self.info.n_repeats}
            Steps: {self.info.init_and_opt_step}
            """
        )


    def get_n_observations(self, step: int | None = None) -> int:

        if step is None:
            return self.info.n_observations

        if step < 1:
            raise ValueError("step must be >= 1")

        if step > self.info.init_and_opt_step:
            raise ValueError(
                f"step={step} exceeds max step "
                f"{self.info.init_and_opt_step}"
            )

        if step == 1:
            return self.info.n_init

        return self.info.n_init + (step - 1) * self.info.n_repeats


    def get_context_at_step(
        self,
        step: int | None = None,) -> OptimizationContext:

        n_obs = self.get_n_observations(step)

        objs = {}
        for name, obj_dict in self.problem["objectives"].items():
            objs[name] = Objective(name, minimize=obj_dict["minimize"])

        ctx = OptimizationContext(
            bounds=self.problem["bounds"],
            objectives=objs,
            inputs=self.problem["inputs"],
        )

        X = self.X_physical[:n_obs]
        Y = self.Y_physical[:n_obs]
        shots = self.shot_numbers[:n_obs]

        for x, y, shot in zip(X, Y, shots):
            ctx.add_observation(
                x=x,
                y=y,
                shot_number=shot,
            )

        ctx.n_init = self.info.n_init

        return ctx


    def get_initial_context(self) -> OptimizationContext:
        return self.get_context_at_step(step=1)


    def get_final_context(self) -> OptimizationContext:
        return self.get_context_at_step()
