# SPDX-License-Identifier: LGPL-2.1-or-later
"""
Turbulent Kinetic Energy (TKE) calculations.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["tke"]


def tke(
    df: pd.DataFrame,
    window_size: int,
    u_col: str = 'u',
    v_col: str = 'v',
    w_col: str = 'w'
) -> tuple[list, list]:
    """
    Calculate Turbulent Kinetic Energy (TKE) in rolling windows.
    
    TKE = 0.5 * (var(u') + var(v') + var(w'))
    
    Args:
        df: DataFrame with datetime index and wind components
        window_size: Number of samples per window (e.g., 10 Hz * 600 s = 6000 for 10 min)
        u_col: Column name for u-component (east-west)
        v_col: Column name for v-component (north-south)
        w_col: Column name for w-component (vertical)
    
    Returns:
        Tuple of (tke_values, time_midpoints)
        - tke_values: List of TKE values for each window (m²/s²)
        - time_midpoints: List of timestamps at the midpoint of each window
    
    Examples:
        >>> # For 10 Hz data with 10-minute windows
        >>> tke_values, times = tke(df, window_size=10*600, u_col='U_m_s', v_col='V_m_s', w_col='W_m_s')
        >>> 
        >>> # For 32 Hz data with 10-minute windows
        >>> tke_values, times = tke(df, window_size=32*600)
    """
    tke_list = []
    time_midpoints = []
    
    for i in range(0, len(df), window_size):
        window = df.iloc[i:i+window_size]
        
        # Skip incomplete windows
        if len(window) < window_size:
            continue
        
        # Compute fluctuations (deviations from mean)
        u_prime = window[u_col] - window[u_col].mean()
        v_prime = window[v_col] - window[v_col].mean()
        w_prime = window[w_col] - window[w_col].mean()
        
        # TKE = 0.5 * sum of variances
        tke = 0.5 * (
            np.var(u_prime, ddof=1) +
            np.var(v_prime, ddof=1) +
            np.var(w_prime, ddof=1)
        )
        
        tke_list.append(tke)
        time_midpoints.append(window.index[window_size // 2])
    
    return tke_list, time_midpoints
