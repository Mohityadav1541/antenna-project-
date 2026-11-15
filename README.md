# Interactive Simulation and Radiation Pattern Control of Linear Antenna Arrays

**Course:** Antennas and Wave Propagation  
**Type:** Python GUI, Simulation, and Analysis  
**Frameworks:** PyQt6, NumPy, SciPy, Matplotlib  

---

## 1. Project Overview

This application is an interactive engineering instrument designed to simulate, visualize, and analyze the radiation characteristics of uniform and non-uniform Linear Antenna Arrays (ULA). 

In accordance with academic requirements, **all principal array-factor computations, closed-form singularity resolutions, numerical metrics, and beam steering calculations are implemented directly from first principles without relying on third-party antenna toolboxes**.

---

## 2. Key Features

- **Interactive Control Panel:**
  - $N$ (Number of elements): 2 to 64 with synchronized slider and spinbox.
  - $d/\lambda$ (Spacing): 0.05 to 2.00 (step 0.01).
  - $\beta$ (Progressive phase): $-360^\circ$ to $+360^\circ$ (step $1^\circ$).
  - Frequency: 0.1 GHz to 30.0 GHz with real-time wavelength $\lambda$ (mm) and physical spacing $d$ (mm) readout.
  - $\theta_0$ (Steering angle): $0^\circ$ to $180^\circ$ with angle slider and bidirectional automatic phase synchronization.
  - Angular resolution: $0.01^\circ$ to $2.00^\circ$.
  - Plot floor: $-100\text{ dB}$ to $-20\text{ dB}$ for display clipping without distorting underlying analytical calculations.
- **Excitation Control (Part F):**
  - Uniform weighting ($a_n = 1$)
  - Binomial weighting ($a_n = \binom{N-1}{n}$)
  - Hann / Cosine-based taper
  - Custom amplitude editor table with live bar graph visualization.
- **Multi-View Radiation Plots:**
  - Cartesian normalized magnitude $|AF_n(\theta)|$ with toggleable markers.
  - Cartesian normalized array factor in decibels ($\text{dB}$) with $-3.01\text{ dB}$ HPBW threshold.
  - Polar radiation pattern with $0^\circ$ aligned along the array axis.
  - 3D axisymmetric radiation pattern revolved around the array axis ($z$).
  - Excitation amplitude weights bar graph.
- **Physical Geometry & Phasor Visualizer (Part G):**
  - Array elements along $z$-axis with physical coordinates and numbering.
  - Excitation phase phasors (arrows and phase wheels).
  - Live constructive / destructive interference indicator along the observation direction.
- **Live Numerical Results Panel (Part E):**
  - Main-beam pointing direction ($\theta_{max}$).
  - Half-Power Beamwidth (HPBW) with sub-pixel interpolation.
  - First-Null Beamwidth (FNBW).
  - Peak Sidelobe Level (SLL in dB).
  - Visible grating-lobe count and angular locations.
  - Spatial phase $kd$ and progressive phase $\beta$ in radians and degrees.
  - Robust handling of boundary beams (reports *"Not defined"* for missing nulls or half-power crossings).
- **Engineering Actions & Utilities:**
  - **Presets:** Reset All, Broadside ($90^\circ$), $+ \text{End-fire}$ ($0^\circ$), $- \text{End-fire}$ ($180^\circ$).
  - **Auto Steer:** Bidirectional coupling between desired direction $\theta_0$ and excitation phase $\beta$.
  - **Steering Animation:** Smooth automated beam sweeping between $20^\circ$ and $160^\circ$.
  - **Pattern Comparison:** Snapshot and overlay reference patterns with active designs.
  - **Exporting:** High-resolution PNG/PDF figures and CSV numerical data.

---

## 3. Mathematical Foundations

### Array Factor Formulations
For an $N$-element array on the $z$-axis with spacing $d$, wavelength $\lambda$, wavenumber $k = 2\pi/\lambda$, progressive excitation phase $\beta$, and observation angle $\theta$:
$$\psi = kd \cos\theta + \beta$$

1. **Direct Complex Exponential Summation (Eq. 2 & Eq. 10):**
   $$AF(\theta) = \sum_{n=0}^{N-1} a_n \exp\left[j (n kd \cos\theta + \phi_n)\right]$$
2. **Closed-Form Solution (Eq. 3):**
   $$AF(\theta) = e^{j(N-1)\psi/2} \frac{\sin(N\psi/2)}{\sin(\psi/2)}$$
3. **Removable Singularity Resolution:**
   When $\psi = 2m\pi$ ($m \in \mathbb{Z}$), $\sin(\psi/2) \to 0$. By L'Hôpital's rule:
   $$\lim_{\psi \to 2m\pi} \frac{\sin(N\psi/2)}{\sin(\psi/2)} = N (-1)^{m(N-1)}$$
   The implementation smoothly evaluates singular points using exact analytical limits without producing `NaN` or `inf`.
4. **Normalized Quantities:**
   $$AF_n(\theta) = \frac{|AF(\theta)|}{\sum_{n=0}^{N-1} a_n}, \quad P_n(\theta) = |AF_n(\theta)|^2, \quad AF_{\text{dB}}(\theta) = 20 \log_{10}(AF_n(\theta))$$

---

## 4. Project Structure

```
antenna project/
├── core/
│   ├── __init__.py
│   ├── physics.py           # Physical constants, lambda, k, spacing, phase conversions
│   ├── array_factor.py      # Summation, closed-form, singularity handling, normalization
│   └── tapering.py          # Uniform, Binomial, Hann, and custom excitation windows
├── analysis/
│   ├── __init__.py
│   ├── pattern_metrics.py   # Analytical & numerical detection of maxima, nulls, HPBW, FNBW, SLL
│   └── steering.py          # Steering phase, pointing angle, and beam tracking
├── gui/
│   ├── __init__.py
│   ├── main_window.py       # Main PyQt6 window and state coordination
│   ├── controls_panel.py    # Sliders, numeric spinboxes, preset buttons
│   ├── plots_widget.py      # Matplotlib canvases (Cartesian, dB, Polar, 3D, Weights)
│   ├── geometry_widget.py   # Array layout, amplitude bars, excitation phasors, interference
│   ├── results_widget.py    # Numerical results cards and status badges
│   └── compare_dialog.py    # Reference pattern overlay dialog
├── export/
│   ├── __init__.py
│   ├── csv_exporter.py      # CSV numerical data exporter
│   └── plot_exporter.py     # PNG/PDF figure exporter
├── experiments/
│   ├── __init__.py
│   └── run_experiments.py   # Generates all 12 publication figures and 3 validation tables
├── output/
│   ├── figures/             # Output PNG figures (Fig 1 through Fig 12)
│   └── tables/              # Markdown/CSV comparison tables (Tables 1, 2, 3)
├── tests/
│   ├── test_array_factor.py # Direct summation vs closed-form tests
│   ├── test_metrics.py      # HPBW interpolation, FNBW, SLL, grating lobes tests
│   ├── test_validation.py   # Verification of all 9 benchmark test cases from Part H
│   └── test_gui.py          # Headless GUI interaction and preset tests
├── requirements.txt
├── README.md
└── main.py                  # Application entry point
```

---

## 5. Installation and Setup

### Prerequisites
- Python 3.9 or higher
- `pip` package manager

### Setup Steps
```bash
# 1. Clone or navigate to the project directory
cd "antenna project"

# 2. Create a virtual environment
python3 -m venv .venv

# 3. Activate the virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

## 6. How to Run

### Interactive GUI Mode
```bash
python main.py
```

### Headless Experiments & Figures Generation
To regenerate all 12 figures and 3 verification tables for reports:
```bash
python experiments/run_experiments.py
```
Outputs are saved directly into `output/figures/` and `output/tables/`.

### Run Test Suite
```bash
pytest tests/
```
All 22 unit tests will execute, verifying mathematical calculations, singularity handling, boundary conditions, and GUI event handling.

---

## 7. Verification and Validation Results (Part H)

The 9 benchmark cases from Section 10 of the assignment specification were tested and verified against analytical solutions:

| Test | $N$ | $d/\lambda$ | $\beta$ | Description | Analytical Prediction | Simulation Result | Absolute Error | HPBW | FNBW |
|:---:|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | 2 | 0.5 | $0^\circ$ | Broadside maximum | $90.0^\circ$ | $90.00^\circ$ | $0.0000^\circ$ | $60.00^\circ$ | $180.00^\circ$ |
| 2 | 4 | 0.5 | $0^\circ$ | Symmetric broadside | $90.0^\circ$ | $90.00^\circ$ | $0.0000^\circ$ | $26.32^\circ$ | $60.00^\circ$ |
| 3 | 8 | 0.5 | $0^\circ$ | Narrower main beam | $90.0^\circ$ | $90.00^\circ$ | $0.0000^\circ$ | $12.80^\circ$ | $28.96^\circ$ |
| 4 | 8 | 0.5 | $-90^\circ$ | Principal beam at $60^\circ$ | $60.0^\circ$ | $60.00^\circ$ | $0.0000^\circ$ | $14.84^\circ$ | $34.11^\circ$ |
| 5 | 8 | 0.5 | $+90^\circ$ | Principal beam at $120^\circ$ | $120.0^\circ$ | $120.00^\circ$ | $0.0000^\circ$ | $14.84^\circ$ | $34.11^\circ$ |
| 6 | 8 | 0.5 | $-180^\circ$ | Positive end-fire | $0.0^\circ$ | $0.00^\circ$ | $0.0000^\circ$ | *Not defined* | *Not defined* |
| 7 | 8 | 0.5 | $+180^\circ$ | Negative end-fire | $180.0^\circ$ | $180.00^\circ$ | $0.0000^\circ$ | *Not defined* | *Not defined* |
| 8 | 8 | 1.0 | $0^\circ$ | Multiple equal-height maxima | $0^\circ, 90^\circ, 180^\circ$ | $90.00^\circ$ | $0.0000^\circ$ | $6.39^\circ$ | $14.36^\circ$ |
| 9 | 16 | 0.5 | $0^\circ$ | Narrower beam than $N=8$ | $90.0^\circ$ | $90.00^\circ$ | $0.0000^\circ$ | $6.36^\circ$ | $14.36^\circ$ |

---

## 8. Originality & Academic Integrity Statement

- **Primary Array Factor Computation:** Implemented from scratch using NumPy vectorization and closed-form limits.
- **Metric Detection:** Analytical root finding cross-validated with numerical peak finding and linear spline interpolation.
- **Third-Party Libraries:** Standard scientific computing stack (`PyQt6`, `numpy`, `scipy`, `matplotlib`, `pytest`). No antenna-specific or black-box simulation libraries were used.
