# libraries
from dataclasses import dataclass

import torch
from botorch.utils.transforms import normalize

# project
from ..core.optimizerContext import OptimizationContext
from ..utils.getter import get_classes
from ..model_construction import StrategyStructure


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

    description: str


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
        
        description = ""
        if "description" in meta.keys():
            description = meta["description"]

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
            description=description
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
            Description: {self.info.description}
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


    def reconstruct_model(self, ctx):
        strategies = get_classes("strategies")

        strategy_cfg = self.data["problem"]["strategy"]
        strategy_cfg_cls = self.data["problem"]["strategy"]["class"]

        strategy = None

        for name, cls in strategies.items():        # loop among the strategies

            # match by class name OR full path
            if strategy_cfg_cls.endswith(name) or strategy_cfg_cls == name:
                strategy = cls()
                break

        if strategy is None:
            raise ValueError(
                f"Unknown strategy: {strategy_cfg}. "
                f"Available: {list(strategies.keys())}"
            )

        model = strategy.build_model(ctx, **strategy_cfg["params"])

        return model, strategy


    def rebuild_model(self, ctx, strategy, strategy_params: dict):
        model = strategy.build_model(ctx, **strategy_params)
        print("Model built.")
        return model


    # def get_posterior(self, 
    #                   ctx: OptimizationContext, 
    #                   x_physical: torch.Tensor) -> tuple[dict, dict, dict]:

    #     model, strategy = self.rebuild_model(ctx)

    #     # model = strategy.load_model(
    #     #     model,
    #     #     self.data["model"]["model_state_dict"]
    #     # )

    #     X_norm = normalize(x_physical, ctx.bounds)

    #     # gathering the objectives names
    #     names = [obj.name for obj in ctx.objectives.values()]
        
    #     post, mean, std = strategy.posterior(
    #         names=names, 
    #         model=model, 
    #         X_norm=X_norm
    #     )

    #     return post, mean, std


    def get_posterior(self,
                    x_physical: torch.Tensor,
                    step: int | None = None):
        
        strategy, strategy_params = self.identify_strategy()

        ctx = self.get_context_at_step(step=step)
        
        # 1) build structure only
        model = self.rebuild_model(ctx, strategy, strategy_params)

        # 2) try restore weights
        model, mode = self._load_model_state(model, step)

        # 3) fallback: fit if nothing saved
        if mode == "none":
            print("Model fitted.")
            model = strategy.fit_model(model)

        # 4) inference input
        X_norm = normalize(x_physical, ctx.bounds)

        names = [obj.name for obj in ctx.objectives.values()]

        post, mean, std = strategy.posterior(
            names=names,
            model=model,
            X_norm=X_norm
        )
        return post, mean, std


    def _load_model_state(self, model, step=None):
        model_data = self.data.get("model", {})
        restaured = "Model state history restaured."
        
        # CASE 1: step-specific history (BEST)
        if step is not None and "model_state_history" in model_data:
            history = model_data["model_state_history"]

            if step in history:
                model.load_state_dict(history[step])
                model.eval()
                print(restaured)
                return model, "history"

        # CASE 2: final state
        if "model_state_dict" in model_data:
            model.load_state_dict(model_data["model_state_dict"])
            model.eval()
            print(restaured)
            return model, "final"

        return model, "none"


    def identify_strategy(self) -> tuple[StrategyStructure, dict]:
        strategies = get_classes("strategies")

        strategy_cfg = self.data["problem"]["strategy"]
        strategy_cfg_cls = self.data["problem"]["strategy"]["class"]

        strategy = None

        for name, cls in strategies.items():        # loop among the strategies

            # match by class name OR full path
            if strategy_cfg_cls.endswith(name) or strategy_cfg_cls == name:
                strategy = cls()
                break

        if strategy is None:
            raise ValueError(
                f"Unknown strategy: {strategy_cfg}. "
                f"Available: {list(strategies.keys())}"
            )
        
        return strategy, strategy_cfg["params"]