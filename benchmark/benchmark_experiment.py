from __future__ import annotations

from typing import Callable
import time
import hashlib
import json

from laplace_log import log

from laplace_opt.core.optimizer import Optimizer

from .starter.convert_opt_to_form_bench import convert_opt_form_bench
from .starter.dummy_server_response_bench import dummy_server_response_bench

from .benchmark_result import BenchmarkResult
from .benchmark_config import BenchmarkConfig


class BenchmarkExperiment:

    def __init__(
            self, 
            config: BenchmarkConfig, 
            target_function: Callable, 
            seed: int):

        self.config = config
        self.seed = seed
        self.target_function = target_function

        self.last_payload = None


    def _capture_candidates(self, payload):
        """Made in order to capture optimizer's candidates."""
        self.last_payload = payload


    def run(self):
        # prepare the opt form
        opt_form = self.config.build_opt_form(
            seed=self.seed, 
            target_function=self.target_function
        )
        opt_form = convert_opt_form_bench(opt_form)

        # create the optimizer
        optimizer = Optimizer(opt_form)

        optimizer.new_candidates.connect(
            self._capture_candidates
        )

        # single / multi mode
        if self.config.is_multi_objective:
            mode = "multi"
        else:
            mode = "single"

        # target function name
        if hasattr(self.target_function, "name"):
            func_name = self.target_function.name 
        else:
            func_name = self.target_function.__name__ 

        # create the result sheet
        result = BenchmarkResult(
            benchmark_name=self.config.name,
            function_name=func_name,
            strategy=self.config.strategy_name,
            acquisition=self.config.acquisition_name,
            seed=self.seed,
            n_inputs=len(opt_form["inputs"]),
            n_objectives=len(opt_form["obj"]),
            mode=mode
        )

        t0 = time.perf_counter()  # start the timer

        optimizer.init_opt()

        if self.last_payload is None:
            raise RuntimeError(
                "Initialization produced no candidates."
            )

        for it in range(self.config.iterations):

            server_reply = dummy_server_response_bench(
                payload=self.last_payload,
                target_function=self.target_function,
            )

            optimizer.update_opt(server_reply)

        elapsed = time.perf_counter() - t0   # compute the elapsed time

        result.elapsed_time = elapsed

        self._fill_result(result, optimizer)  # fill the result sheet

        return result


    def _fill_result(
        self,
        result: BenchmarkResult,
        optimizer: Optimizer):

        context = optimizer.context

        # observations
        for i, obs in enumerate(context._observations):

            y_opt = obs.y

            y_phys = context._to_physical(
                y_opt.unsqueeze(0)
            )[0]


            result.add_observation(
                x=obs.x,

                y_physical=y_phys,

                y_opt=y_opt,

                iteration=max(
                    0,
                    i - context.n_init
                ),

                is_init=(
                    i < context.n_init
                ),

                shot_number=obs.shot_number,
            )


        result.add_problem(

            bounds=context.bounds.tolist(),

            inputs=context.get_input_state_dict(),

            objectives=context.get_obj_state_dict(),

        )


        result.add_metadata(

            n_init=context.n_init,

            n_total=len(context._observations),

        )


        # reproducibility fingerprint
        opt_form = self.config.build_opt_form(
            seed=self.seed,
            target_function=self.target_function
        )

        config_hash = hashlib.sha256(
            json.dumps(
                opt_form,
                sort_keys=True,
                default=str,
            ).encode()
        ).hexdigest()


        result.add_metadata(

            config_hash=config_hash,

        )


        # optimizer decisions
        try:

            result.add_metadata(

                suggestions=[
                    s.tolist()
                    for s in optimizer.suggestion_history
                ]

            )

        except Exception:

            pass


        try:

            result.add_metrics(

                pareto=
                    context.get_pareto_front_physical()
                    .tolist()

            )

        except Exception:

            pass


        try:

            result.add_metrics(

                best_results=
                    optimizer.compute_best_results()

            )

        except Exception:

            pass


    @staticmethod
    def replay(result):

        return result.dataframe