# SPDX-License-Identifier: LGPL-2.1-or-later
"""
Eddy (fluctuation) calculations for turbulent flux analysis.
"""
from __future__ import annotations

import pandas as pd

__all__ = ["fluctuations"]


def fluctuations(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """
    Compute fluctuations (deviations from mean) for specified columns.
    
    This calculates the turbulent fluctuation components (e.g., u', v', w', T')
    by subtracting the mean from each variable within each time window.
    
    Args:
        df: DataFrame with variables to compute fluctuations for
        columns: List of column names to compute fluctuations. 
                 If None, computes for all numeric columns.
    
    Returns:
        DataFrame with fluctuation values (same index as input)
        Column names will have '_prime' suffix (e.g., 'u' -> 'u_prime')
    
    Examples:
        >>> df_fluctuations = fluctuations(df, columns=['u', 'v', 'w', 'T'])
        >>> # Returns df with columns: u_prime, v_prime, w_prime, T_prime
    """
    if columns is None:
        columns = df.select_dtypes(include='number').columns.tolist()
    
    df_prime = pd.DataFrame(index=df.index)
    
    for col in columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame")
        df_prime[f"{col}_prime"] = df[col] - df[col].mean()
    
    return df_prime
