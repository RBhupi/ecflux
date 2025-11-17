# ecflux

> A lightweight Python package for turbulent flux calculations using the eddy covariance method.

## Overview

`ecflux` provides functions for computing turbulent fluxes from high-frequency meteorological data. It is without most bells and whistles and it's designed for basic flux computations.

**Note:** This package currently does not include comprehensive quality assurance/quality control (QAQC) procedures. We are planning to add more QAQC modules for spike removal, despiking, smoothing, and quality testing in future releases. **Contributions are welcome!**

## Acknowledgment

This package is based on code developed during Julie Piot's summer internship project at Argonne National Laboratory, funded by the U.S. Department of Energy (DOE). Original Project repository: [summer2025/Julie_Piot](https://github.com/RBhupi/summer2025/tree/main/Julie_Piot)

## Installation

```bash
# Local installation in editable mode
pip install -e .
```

## Quick Start

```python
import pandas as pd
from ecflux import ecflux, tke

# Load your high-frequency data (must have datetime index)
df = pd.read_csv('your_data.csv')
df.index = pd.to_datetime(df['timestamp'])

# Compute sensible heat flux (30-minute windows)
H = ecflux(df, w='W_m_s', scalar='T_C', flux='H', freq='30T')

# Compute latent heat flux
LE = ecflux(df, w='W_m_s', scalar='q', flux='L', freq='30T')

# Compute momentum flux
tau = ecflux(df, w='W_m_s', flux='Tau', freq='30T', u='U_m_s', v='V_m_s')

# Compute TKE (10-minute windows at 10 Hz)
tke_values, times = tke(df, window_size=6000, u='U_m_s', v='V_m_s', w='W_m_s')
```

## Main Functions

### ecflux() - Unified Flux Calculation Interface

The primary user-facing function for computing turbulent fluxes:

```python
from ecflux import ecflux

# Sensible heat flux: H = rho * cp * <w' T'>
H = ecflux(df, w='W_m_s', scalar='T_C', flux='H', freq='30T', rho=1.2, cp=1005)

# Latent heat flux: LE = rho * Lv * <w' q'>
LE = ecflux(df, w='W_m_s', scalar='q', flux='L', freq='30T', rho=1.2, Lv=2.5e6)

# Momentum flux: tau = rho * sqrt(<u'w'>² + <v'w'>²)
tau = ecflux(df, w='W_m_s', flux='Tau', freq='30T', u='U_m_s', v='V_m_s', rho=1.2)
```

**Parameters:**
- `raw_df`: DataFrame with datetime index containing raw high-frequency data
- `w`: Column name for vertical wind velocity (m/s)
- `scalar`: Column name for scalar variable (temperature, humidity, etc.) - not needed for Tau
- `flux`: Type of flux - `'H'` (sensible heat), `'L'` or `'LE'` (latent heat), `'Tau'` (momentum)
- `freq`: Time window for averaging (e.g., `'30T'` for 30 minutes)
- `rho`: Air density (kg/m³), default 1.2
- `cp`: Specific heat capacity (J/kg/K), default 1005
- `Lv`: Latent heat of vaporization (J/kg), default 2.5e6

### tke() - Turbulent Kinetic Energy

```python
from ecflux import tke

# For 10 Hz data with 10-minute windows
tke_values, times = tke(df, window_size=6000, u='U_m_s', v='V_m_s', w='W_m_s')

# For 20 Hz data with 5-minute windows
tke_values, times = tke(df, window_size=6000, u='u', v='v', w='w')
```

**Parameters:**
- `raw_df`: DataFrame with datetime index
- `window_size`: Number of samples per window (frequency × seconds)
- `u`, `v`, `w`: Column names for wind components

**Returns:**
- `tke_values`: List of TKE values (m²/s²)
- `times`: List of timestamps at window midpoints

## Advanced Usage

For advanced users and QAQC module development, lower-level functions are available:

```python
from ecflux import covariance_flux, fluctuations

# Generic covariance calculation (foundation of eddy covariance)
flux = covariance_flux(df, vertical_var='w', scalar_var='CO2', freq='30T', scale_factor=1.0)

# Extract turbulent fluctuations
df_prime = fluctuations(df, columns=['u', 'v', 'w', 'T'])
# Returns DataFrame with columns: u_prime, v_prime, w_prime, T_prime
```

## Data Requirements

Your DataFrame must:
- Have a datetime index
- Contain the required columns (wind components, temperature, etc.)
- Be at high frequency (typically 10-32 Hz for flux measurements)


## Future Development

This package is designed with extensibility in mind. Planned additions include:

### QAQC Modules (High Priority)
- Spike detection and removal algorithms
- Despiking methods (median filter, MAD-based, etc.)
- Data smoothing and filtering
- Quality flags and automated quality testing
- Missing data handling and gap filling

### Additional Features
- Additional flux types and corrections (storage fluxes, spectral corrections)
- Coordinate rotation methods (planar fit, double rotation)
- Frequency response corrections
- Footprint analysis integration
- WPL (Webb-Pearman-Leuning) corrections for trace gas fluxes

## Contributing

**Contributions are welcome!** If you'd like to contribute:
- Fork the repository
- Create a feature branch
- Submit a pull request

Areas where contributions would be particularly valuable:
- QAQC algorithms and methods
- Unit tests and validation against known datasets
- Documentation improvements
- Additional flux calculation methods
- Performance optimizations


