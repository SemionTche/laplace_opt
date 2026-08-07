from __future__ import annotations

import time
import json

from laplace_opt.core.optimizer import Optimizer

from ..starter.convert_opt_to_form_bench import convert_opt_form_bench
from ..starter.dummy_server_response_bench import dummy_server_response_bench
from ..functions.base import TestFunction

from .benchmark_result import BenchmarkResult
from .benchmark_config import BenchmarkConfig


class BenchmarkExperiment:

    def __init__(self, 
                 config: BenchmarkConfig, 
                 target_function: TestFunction, 
                 seed: int):

        self.config = config
        self.seed = seed
        self.target_function = target_function

        # target function name
        if hasattr(self.target_function, "name"):
            self.func_name = self.target_function.name 
        else:
            self.func_name = self.target_function.__name__ 

        self.last_payload = None


    def _capture_candidates(self, payload) -> None:
        """Capture optimizer's suggestions."""
        self.last_payload = payload


    def run(self) -> BenchmarkResult:
        """
        Run a benchmark experiment. 
        
            Return:
                BenchmarkResult
        """
        ### prepare the opt form
            # fill the target function and the seed
            # with the corresponding attribute of
            # the experiment
        opt_form = self.config.build_opt_form(
            target_function=self.target_function,
            seed=self.seed, 
        )
            # convert the features from human dict
            # to corresponding classes for optimizer
            # compatibility
        opt_form = convert_opt_form_bench(opt_form)

        # create the optimizer
        optimizer = Optimizer(opt_form)

        # capture the suggestions
        optimizer.new_candidates.connect(
            self._capture_candidates
        )

        # create the result sheet
        result = BenchmarkResult(

            benchmark_name=self.config.name,

            function_name=self.func_name,

            strategy=self.config.strategy_name,

            acquisition=self.config.acquisition_name,

            seed=self.seed,

            n_inputs=len(opt_form["inputs"]),

            n_objectives=len(opt_form["obj"]),

        )

        t0 = time.perf_counter()  # start the timer

        optimizer.init_opt()      # generate the init candidates

        if self.last_payload is None:  # if the last_payload did not catch the candidates
            raise RuntimeError(
                "Initialization produced no candidates."
            )


        for it in range(self.config.iterations):   # for each opt iteration

            # sample the candidates
            server_reply = dummy_server_response_bench(
                payload=self.last_payload,
                target_function=self.target_function,
            )

            # send the values to the optimizer
            optimizer.update_opt(server_reply)

            # add the current state of the model
            self.capture_model_snapshot(
                iteration=it,
                result=result,
                optimizer=optimizer,
            )

            # add the current state of acquisition
            result.add_acquisition_state(
                iteration=it,
                acquisition=optimizer.acquisition,
            )

        # elapsed time in seconde
        result.finish()

        if len(result.model_history) == 0:     # if the model was not catched
            raise RuntimeError(
                "No model snapshots were saved during benchmark execution"
            )

        self._fill_result(        # fill the rest of the result
            result=result, 
            optimizer=optimizer
        )

        return result


    def capture_model_snapshot(self,
                               iteration: int,
                               result: BenchmarkResult,
                               optimizer: Optimizer,) -> None:
        """
        Add the current model to the result.
        """
        model = optimizer.model
        train_X = optimizer.context.X_physical
        train_Y = optimizer.context.Y_physical

        result.add_model_snapshot(
            iteration=iteration,
            model=model,
            train_X=train_X,
            train_Y=train_Y,
        )


    def _fill_result(self,
                     result: BenchmarkResult,
                     optimizer: Optimizer) -> None:
        """
        Complete the result with the relevant elements.
        """
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

                iteration=max( 0, i - context.n_init ),

                is_init=( i < context.n_init ),

                shot_number=obs.shot_number,
            )

        # static info
        result.add_problem(
            bounds=context.bounds.tolist(),

            inputs=context.get_input_state_dict(),

            objectives=context.get_obj_state_dict(),

            optimum_input=self.target_function.optimum_input,

            optimum_obj=self.target_function.optimum_obj.item()
        )

        # metadata
        opt_form = self.config.build_opt_form(
            target_function=self.target_function,
            seed=self.seed,
        )

        config_json = json.dumps(
            opt_form,
            sort_keys=True,
            default=str,
        )

        result.add_metadata(
            n_init=context.n_init,

            n_total=len(context._observations),

            config_json=config_json,

            suggestions=[
                    s.tolist()
                    for s in optimizer.suggestion_history
                ]
        )

        # best results
        # result.add_metrics(
        #     best_results = 
        #         optimizer.compute_best_results()
        # )

    @staticmethod
    def replay(result):
        return result.dataframe