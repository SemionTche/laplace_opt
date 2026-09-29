import numpy as np

def norm_curve(
                curve: np.ndarray,
                normalization: str | None = None,) -> np.ndarray:
    """
    Normalize a curve.

    Parameters
    ----------
    normalization
        None        : return unchanged
        "relative"  : divide by first value
    """
    if normalization is None:
        return curve

    if normalization == "relative":
        ref = curve[0]

        if np.isclose(ref, 0):
            return np.zeros_like(curve)

        return curve / ref

    raise ValueError(
        f"Unknown normalization '{normalization}'."
    )