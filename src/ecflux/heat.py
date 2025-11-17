# SPDX-License-Identifier: LGPL-2.1-or-later
"""
Sensible heat flux calculations.
"""
from __future__ import annotations

import pandas as pd
from .covariance import covariance_flux

__all__ = ["sensible_heat_flux"]


def sensible_heat_flux(
    df: pd.DataFrame,
    freq: str = '30T',
    var_col: str = 'T_C',
    wind_col: str = 'W_m_s',
    rho: float = 1.2,
    cp: float = 1005
) -> pd.Series:
    """
    Compute sensible heat flux (H) using eddy covariance method.
    
    H = rho * cp * <w' T'>
    
    where:
    - rho is air density (kg/m³)
    - cp is specific heat capacity of air (J/kg/K)
    - <w' T'> is the covariance between vertical wind and temperature
    
    Args:
        df: DataFrame with datetime index
        freq: Time window for averaging (e.g., '30T' for 30 minutes)
        var_col: Column name for temperature (e.g., 'T_C')
        wind_col: Column name for vertical wind (e.g., 'W_m_s')
        rho: Air density (kg/m³), default 1.2
        cp: Specific heat capacity (J/kg/K), default 1005
    
    Returns:
        Series of sensible heat flux values (W/m²) indexed by time window
    
    Examples:
        >>> H = sensible_heat_flux(df, freq='30T', var_col='T_C', wind_col='W_m_s')
    """
    scale_factor = rho * cp
    return covariance_flux(df, wind_col, var_col, freq, scale_factor)
