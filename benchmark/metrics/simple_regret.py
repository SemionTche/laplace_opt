from .metric import Metric


class SimpleRegret(Metric):

    name = "simple_regret"
    relative_name = "simple_regret_rel"

    def compute(self, analyzer):

        return float(
            analyzer.regret_curve()[-1]
        )

    def compute_relative(self, analyzer):

        return float(
            analyzer.regret_curve_relative()[-1]
        )