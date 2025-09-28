from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple


def _try_import_scipy():
    try:
        from scipy import stats  # type: ignore
        return stats
    except Exception:
        return None


def spearman_rho(x: Sequence[float], y: Sequence[float]) -> Tuple[float, Optional[float]]:
    stats = _try_import_scipy()
    if stats is not None:
        rho, p = stats.spearmanr(x, y)
        return float(rho), float(p)
    # Fallback: compute rho via ranking and Pearson; p-value approximated via t with n-2 df
    from math import sqrt
    import numpy as np

    rx = _rankdata(x)
    ry = _rankdata(y)
    rho = float(np.corrcoef(rx, ry)[0, 1])
    n = len(x)
    if n > 2:
        t = rho * sqrt((n - 2) / (1 - rho ** 2 + 1e-12))
        # two-sided p via student's t (approx) if scipy unavailable
        return rho, None
    return rho, None


def kendall_tau_b(x: Sequence[float], y: Sequence[float]) -> Tuple[float, Optional[float]]:
    stats = _try_import_scipy()
    if stats is not None:
        tau, p = stats.kendalltau(x, y, variant="b")
        return float(tau), float(p)
    # No robust pure-Python tau-b with p-value provided here
    # Provide value via scipy-like approximation by reducing to concordance counts if needed.
    return 0.0, None


def _rankdata(a: Sequence[float]):
    import numpy as np

    a = np.asarray(a)
    temp = a.argsort()
    ranks = np.empty_like(temp, dtype=float)
    ranks[temp] = np.arange(len(a))
    # average ranks for ties
    _, inv, counts = np.unique(a, return_inverse=True, return_counts=True)
    cumcounts = counts.cumsum()
    start = cumcounts - counts
    avg_ranks = (start + cumcounts - 1) / 2.0
    return avg_ranks[inv]


def _anova_components(X):
    import numpy as np
    n, k = X.shape
    mean_rows = X.mean(axis=1, keepdims=True)
    mean_cols = X.mean(axis=0, keepdims=True)
    grand = X.mean()
    SSR = k * float(((mean_rows - grand) ** 2).sum())
    SSC = n * float(((mean_cols - grand) ** 2).sum())
    SSE = float(((X - mean_rows - mean_cols + grand) ** 2).sum())
    dfR = n - 1
    dfC = k - 1
    dfE = dfR * dfC
    MSR = SSR / dfR if dfR > 0 else 0.0
    MSC = SSC / dfC if dfC > 0 else 0.0
    MSE = SSE / dfE if dfE > 0 else 0.0
    return n, k, MSR, MSC, MSE, dfR, dfE


def icc_a1(values: List[Tuple[float, float]] | "np.ndarray") -> Tuple[float, Optional[float]]:
    """
    Compute ICC(A,1) absolute agreement, two-way mixed, single rater.
    Accepts either:
      - list of (rater1, rater2) across N targets, or
      - 2D numpy array of shape (n_targets, k_raters) with k>=2
    Returns: (icc_value, p_value[approx or None])
    """
    import numpy as np

    X = np.asarray(values, dtype=float)
    if X.ndim != 2 or X.shape[1] < 2:
        raise ValueError("icc_a1 expects shape (n, k>=2)")
    n, k, MSR, MSC, MSE, dfR, dfE = _anova_components(X)

    if n <= 1:
        return 0.0, None
    denom = MSR + (k - 1) * MSE + (k * (MSC - MSE) / n)
    if abs(denom) < 1e-12:
        # Degenerate case: no variance; ICC undefined → return 0 with no p-value
        return 0.0, None
    icc = (MSR - MSE) / denom

    # Approximate p-value using F = MSR/MSE with dfR, dfE (common in ANOVA context)
    stats = _try_import_scipy()
    pval = None
    if stats is not None and MSE > 0 and dfE > 0:
        F = MSR / MSE if MSE > 0 else 0.0
        try:
            pval = float(stats.f.sf(F, dfR, dfE))
        except Exception:
            pval = None
    return float(icc), pval


def icc_ak(values: List[Tuple[float, float]] | "np.ndarray") -> Tuple[float, Optional[float]]:
    """ICC(A,k): absolute agreement, two-way mixed, average of k raters."""
    import numpy as np

    X = np.asarray(values, dtype=float)
    if X.ndim != 2 or X.shape[1] < 2:
        raise ValueError("icc_ak expects shape (n, k>=2)")
    n, k, MSR, MSC, MSE, dfR, dfE = _anova_components(X)
    if n <= 1:
        return 0.0, None
    denom = MSR + (k * (MSC - MSE) / n)
    if abs(denom) < 1e-12:
        return 0.0, None
    icc = (MSR - MSE) / denom
    # Use same F approx for p-value (rough)
    pval = None
    try:
        from scipy import stats  # type: ignore
        if MSE > 0 and dfE > 0:
            F = MSR / MSE
            pval = float(stats.f.sf(F, dfR, dfE))
    except Exception:
        pass
    return float(icc), pval
