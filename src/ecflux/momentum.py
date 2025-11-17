# SPDX-License-Identifier: LGPL-2.1-or-later
"""
Momentum flux (wind stress) calculations.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["momentum_flux"]


def momentum_flux(
    df: pd.DataFrame,
    freq: str = '30T',
    u_col: str = 'U_m_s',
    v_col: str = 'V_m_s',
    w_col: str = 'W_m_s',
    rho: float = 1.2
) -> pd.Series:
    """
    Compute momentum flux (tau) using eddy covariance method.
    
    tau = rho * sqrt(<u'w'>² + <v'w'>²)
    
    where:
    - rho is air density (kg/m³)
    - <u'w'> is the covariance between horizontal (u) and vertical (w) wind
    - <v'w'> is the covariance between horizontal (v) and vertical (w) wind
    
    Args:
        df: DataFrame with datetime index and wind components
        freq: Time window for averaging (e.g., '30T' for 30 minutes)
        u_col: Column name for u-component (east-west)
        v_col: Column name for v-component (north-south)
        w_col: Column name for w-component (vertical)
        rho: Air density (kg/m³), default 1.2
    
    Returns:
        Series of momentum flux values (N/m² or kg/m/s²) indexed by time window
    
    Examples:
        >>> tau = momentum_flux(df, freq='30T', u_col='U_m_s', v_col='V_m_s', w_col='W_m_s')
    """
    df = df[[u_col, v_col, w_col]].dropna()
    
    def compute_tau_window(g):
        """Compute momentum flux for a single time window."""
        u_prime = g[u_col] - g[u_col].mean()
        v_prime = g[v_col] - g[v_col].mean()
        w_prime = g[w_col] - g[w_col].mean()
        
        uw_cov = (u_prime * w_prime).mean()
        vw_cov = (v_prime * w_prime).mean()
        
        tau = rho * np.sqrt(uw_cov**2 + vw_cov**2)
        return tau
    
    tau_series = df.groupby(pd.Grouper(freq=freq)).apply(compute_tau_window)
    tau_series.name = 'tau_N_per_m2'
    
    return tau_series
