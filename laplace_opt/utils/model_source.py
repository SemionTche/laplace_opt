from pathlib import Path


class ModelSource:
    """
    Resolve the model_construction directory used by the application.

    If an external path is provided, it is used.
    Otherwise, the model_construction directory shipped with the application
    is used.
    """

    def __init__(self, external_path: str = ""):
        if external_path:
            self.external_path = Path(external_path).expanduser()
            self.is_external = True
        else:
            self.external_path = Path(__file__).resolve().parent.parent / "model_construction"
            self.is_external = False
        self.validate()


    @property
    def root(self) -> Path:
        return self.external_path

    @property
    def inputs(self) -> Path:
        return self.root / "inputs"

    @property
    def objectives(self) -> Path:
        return self.root / "objectives"

    @property
    def initializations(self) -> Path:
        return self.root / "initializations"

    @property
    def strategies(self) -> Path:
        return self.root / "strategies"

    @property
    def acquisitions(self) -> Path:
        return self.root / "acquisitions"

    @property
    def config(self) -> Path:
        return self.root / "config.ini"

    def validate(self) -> None:
        if not self.root.is_dir():
            raise FileNotFoundError(
                f"model_construction directory does not exist: {self.root}"
            )