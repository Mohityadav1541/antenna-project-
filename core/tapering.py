"""
Amplitude taper functions for antenna arrays (Part F).
Implements:
- Uniform weighting
- Binomial weighting
- Cosine-based taper (Hann)
- Custom weighting
"""

from typing import List, Union
import numpy as np
from scipy.special import comb


def get_uniform_weights(N: int) -> np.ndarray:
    """All elements have equal amplitude 1.0."""
    return np.ones(N, dtype=np.float64)


def get_binomial_weights(N: int) -> np.ndarray:
    """
    Binomial weighting:
    a_n = comb(N-1, n) for n = 0, ..., N-1.
    Yields very low (theoretically zero) sidelobes at d <= 0.5 lambda,
    at the cost of wider main beamwidth.
    """
    n_idx = np.arange(N)
    weights = comb(N - 1, n_idx, exact=False)
    # Normalize peak weight to 1.0 for convenient display/control
    return weights / np.max(weights)


def get_hann_weights(N: int) -> np.ndarray:
    """
    Cosine-based taper (Hann window):
    w_n = 0.5 - 0.5 * cos(2 * pi * (n + 0.5) / N)
    Symmetric taper providing significant sidelobe suppression.
    """
    n_idx = np.arange(N)
    # Periodic Hann formulation ensuring non-zero endpoints
    weights = 0.5 * (1.0 - np.cos(2.0 * np.pi * (n_idx + 0.5) / N))
    return weights / np.max(weights)


def get_weights_by_type(weight_type: str, N: int, custom_weights: Union[List[float], np.ndarray, None] = None) -> np.ndarray:
    """Factory function for excitation weights."""
    t = weight_type.lower().strip()
    if t == "uniform":
        return get_uniform_weights(N)
    elif t == "binomial":
        return get_binomial_weights(N)
    elif t in ("hann", "cosine"):
        return get_hann_weights(N)
    elif t == "custom":
        if custom_weights is None or len(custom_weights) != N:
            return get_uniform_weights(N)
        w = np.asarray(custom_weights, dtype=np.float64)
        max_w = np.max(np.abs(w))
        return w / max_w if max_w > 0 else np.ones(N)
    else:
        raise ValueError(f"Unknown weight type: {weight_type}. Choose from 'uniform', 'binomial', 'hann', 'custom'.")
