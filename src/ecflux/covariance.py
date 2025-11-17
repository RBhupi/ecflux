# SPDX-License-Identifier: LGPL-2.1-or-later
"""
Generic covariance flux calculations.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["covariance_flux"]


def covariance_flux(
    df: pd.DataFrame,
    vertical_var: str,
    scalar_var: str,
    freq: str = '30T',
    scale_factor: float = 1.0
) -> pd.Series:
    """
    Compute turbulent flux as covariance between vertical wind and any scalar.
    
    This is the core eddy covariance calculation: flux = <w' * C'>
    where w' is vertical wind fluctuation and C' is scalar fluctuation.
    
    Args:
        df: DataFrame with datetime index containing the variables
        vertical_var: Column name for vertical wind (typically 'w' or 'W_m_s')
        scalar_var: Column name for scalar quantity (e.g., 'T', 'q', 'CO2')
        freq: Time window for averaging (e.g., '30T' for 30 minutes)
        scale_factor: Multiplicative factor for unit conversion (e.g., rho*cp for heat flux)
    
    Returns:
        Series of flux values indexed by time window
    
    Examples:
        >>> # Sensible heat flux
        >>> H = covariance_flux(df, 'w', 'T', freq='30T', scale_factor=rho*cp)
        >>> 
        >>> # Latent heat flux
        >>> LE = covariance_flux(df, 'w', 'q', freq='30T', scale_factor=rho*Lv)
        >>> 
        >>> # CO2 flux
        >>> Fc = covariance_flux(df, 'w', 'CO2', freq='30T')
    """
    df = df[[vertical_var, scalar_var]].dropna()
    
    def compute_window_covariance(g):
        """Compute covariance for a single time window."""
        w_prime = g[vertical_var] - g[vertical_var].mean()
        c_prime = g[scalar_var] - g[scalar_var].mean()
        return np.mean(w_prime * c_prime)
    
    flux = df.groupby(pd.Grouper(freq=freq)).apply(compute_window_covariance)
    flux.name = f"{scalar_var}_flux"
    
    return flux * scale_factor
