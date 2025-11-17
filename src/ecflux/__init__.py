# SPDX-License-Identifier: LGPL-2.1-or-later
"""
ecflux - Simple turbulent flux calculations using eddy covariance
A lightweight package for basic eddy covariance flux computations

Main user-facing functions:
    - ecflux(): Calculate turbulent fluxes (sensible heat, latent heat, momentum)
    - tke(): Calculate turbulent kinetic energy

Lower-level functions (for advanced users and QAQC modules):
    - covariance_flux(): Generic covariance calculation
    - fluctuations(): Compute turbulent fluctuations
"""
from __future__ import annotations

__version__ = "0.1.0"

# Main user-facing API
from .flux import ecflux, tke

# Lower-level functions (available for advanced use and QAQC)
from .eddy import fluctuations
from .covariance import covariance_flux

# For backwards compatibility (will be deprecated)
from .heat import sensible_heat_flux
from .momentum import momentum_flux

__all__ = [
    # Primary user API
    "ecflux",
    "tke",
    # Lower-level functions
    "fluctuations",
    "covariance_flux",
    # Package metadata
    "__version__",
]

