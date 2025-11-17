# SPDX-License-Identifier: LGPL-2.1-or-later
"""
High-level user-facing functions for turbulent flux calculations.
These are the main functions users should call.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["ecflux", "tke"]


def ecflux(
    raw_df: pd.DataFrame,
    w: str = 'w',
    scalar: str | None = None,
    flux: str = 'H',
    freq: str = '30T',
    rho: float = 1.2,
    cp: float = 1005.0,
    Lv: float = 2.5e6,
    **kwargs
) -> pd.Series:
    """
    Compute turbulent fluxes using eddy covariance method.
    
    This is the main user-facing function for flux calculations.
    It handles different flux types (sensible heat, latent heat, momentum)
    and calls the appropriate lower-level calculation functions.
    
    Args:
        raw_df: DataFrame with datetime index containing raw high-frequency data
        w: Column name for vertical wind velocity (m/s)
        scalar: Column name for scalar variable (temperature, humidity, etc.)
                For momentum flux (Tau), this is ignored
        flux: Type of flux to calculate:
              - 'H': Sensible heat flux (W/m²)
              - 'L' or 'LE': Latent heat flux (W/m²)
              - 'Tau': Momentum flux (N/m²)
        freq: Time window for averaging (e.g., '30T' for 30 minutes)
        rho: Air density (kg/m³), default 1.2
        cp: Specific heat capacity of air (J/kg/K), default 1005
        Lv: Latent heat of vaporization (J/kg), default 2.5e6
        **kwargs: Additional arguments passed to specific flux calculations
                  For Tau: u='u', v='v' (horizontal wind components)
    
    Returns:
        Series of flux values indexed by time window
    
    Examples:
        >>> # Sensible heat flux
        >>> H = ecflux(df, w='W_m_s', scalar='T_C', flux='H', freq='30T')
        >>> 
        >>> # Latent heat flux
        >>> LE = ecflux(df, w='W_m_s', scalar='q', flux='L', freq='30T')
        >>> 
        >>> # Momentum flux
        >>> tau = ecflux(df, w='W_m_s', flux='Tau', freq='30T', u='U_m_s', v='V_m_s')
    """
    flux = flux.upper()
    
    if flux == 'H':
        # Sensible heat flux: H = rho * cp * <w' T'>
        if scalar is None:
            raise ValueError("scalar (temperature) must be specified for sensible heat flux")
        return _sensible_heat_flux(raw_df, freq, scalar, w, rho, cp)
    
    elif flux in ('L', 'LE'):
        # Latent heat flux: LE = rho * Lv * <w' q'>
        if scalar is None:
            raise ValueError("scalar (specific humidity) must be specified for latent heat flux")
        return _latent_heat_flux(raw_df, freq, scalar, w, rho, Lv)
    
    elif flux == 'TAU':
        # Momentum flux: tau = rho * sqrt(<u'w'>² + <v'w'>²)
        u_col = kwargs.get('u', 'u')
        v_col = kwargs.get('v', 'v')
        return _momentum_flux(raw_df, freq, u_col, v_col, w, rho)
    
    else:
        raise ValueError(f"Unknown flux type: {flux}. Use 'H', 'L'/'LE', or 'Tau'")


def tke(
    raw_df: pd.DataFrame,
    window_size: int,
    u: str = 'u',
    v: str = 'v',
    w: str = 'w'
) -> tuple[list, list]:
    """
    Calculate Turbulent Kinetic Energy (TKE) in rolling windows.
    
    TKE = 0.5 * (var(u') + var(v') + var(w'))
    
    This is the main user-facing function for TKE calculations.
    
    Args:
        raw_df: DataFrame with datetime index containing raw high-frequency wind data
        window_size: Number of samples per window (e.g., 10 Hz * 600 s = 6000 for 10 min)
        u: Column name for u-component (east-west wind, m/s)
        v: Column name for v-component (north-south wind, m/s)
        w: Column name for w-component (vertical wind, m/s)
    
    Returns:
        Tuple of (tke_values, time_midpoints)
        - tke_values: List of TKE values for each window (m²/s²)
        - time_midpoints: List of timestamps at the midpoint of each window
    
    Examples:
        >>> # For 10 Hz data with 10-minute windows
        >>> tke_values, times = tke(df, window_size=10*600, u='U_m_s', v='V_m_s', w='W_m_s')
        >>> 
        >>> # For 20 Hz data with 5-minute windows
        >>> tke_values, times = tke(df, window_size=20*300)
    """
    tke_list = []
    time_midpoints = []
    
    for i in range(0, len(raw_df), window_size):
        window = raw_df.iloc[i:i+window_size]
        
        # Skip incomplete windows
        if len(window) < window_size:
            continue
        
        # Compute fluctuations (deviations from mean)
        u_prime = window[u] - window[u].mean()
        v_prime = window[v] - window[v].mean()
        w_prime = window[w] - window[w].mean()
        
        # TKE = 0.5 * sum of variances
        tke_val = 0.5 * (
            np.var(u_prime, ddof=1) +
            np.var(v_prime, ddof=1) +
            np.var(w_prime, ddof=1)
        )
        
        tke_list.append(tke_val)
        time_midpoints.append(window.index[window_size // 2])
    
    return tke_list, time_midpoints


# ============================================================================
# Internal helper functions (called by ecflux)
# ============================================================================

def _sensible_heat_flux(
    df: pd.DataFrame,
    freq: str,
    var_col: str,
    wind_col: str,
    rho: float,
    cp: float
) -> pd.Series:
    """
    Internal: Compute sensible heat flux (H) using eddy covariance method.
    
    H = rho * cp * <w' T'>
    """
    from .covariance import covariance_flux
    scale_factor = rho * cp
    flux = covariance_flux(df, wind_col, var_col, freq, scale_factor)
    flux.name = 'H_W_per_m2'
    return flux


def _latent_heat_flux(
    df: pd.DataFrame,
    freq: str,
    var_col: str,
    wind_col: str,
    rho: float,
    Lv: float
) -> pd.Series:
    """
    Internal: Compute latent heat flux (LE) using eddy covariance method.
    
    LE = rho * Lv * <w' q'>
    """
    from .covariance import covariance_flux
    scale_factor = rho * Lv
    flux = covariance_flux(df, wind_col, var_col, freq, scale_factor)
    flux.name = 'LE_W_per_m2'
    return flux


def _momentum_flux(
    df: pd.DataFrame,
    freq: str,
    u_col: str,
    v_col: str,
    w_col: str,
    rho: float
) -> pd.Series:
    """
    Internal: Compute momentum flux (tau) using eddy covariance method.
    
    tau = rho * sqrt(<u'w'>² + <v'w'>²)
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
