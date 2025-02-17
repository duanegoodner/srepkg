import numpy as np


def add_flattened_arrays(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Flattens two numpy arrays and adds them together.
    Args:
        a: a numpy array
        b: a numpy array

    Returns:
        Sum of flattened versions of the two arrays.

    Raises:
        TypeError: if `a` and `b` do not have same data type.
        ValueError: if flattened versions of `a` and `b` do not have same data
        shape.

    """
    if a.dtype != b.dtype:
        raise TypeError("arrays must have the same dtype")

    flattened_a = a.flatten()
    flattened_b = b.flatten()

    if flattened_a.shape != flattened_b.shape:
        raise ValueError("Flattened arrays must have the same shape")

    return flattened_a + flattened_b

