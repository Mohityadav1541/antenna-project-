"""
Vercel Serverless Function for Linear Antenna Array Simulation API.
Endpoint: /api/simulate
Accepts GET or POST requests with simulation parameters and returns complete numerical analysis and radiation pattern data.
"""

from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import sys
from pathlib import Path
import numpy as np

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.physics import frequency_to_wavelength, physical_spacing_mm
from core.array_factor import compute_normalized_pattern
from core.tapering import get_weights_by_type
from analysis.pattern_metrics import compute_pattern_metrics
from analysis.steering import compute_steering_phase, compute_achieved_angle


def run_simulation(params: dict) -> dict:
    N = int(params.get("N", 8))
    N = max(2, min(64, N))

    d = float(params.get("d_over_lambda", 0.50))
    d = max(0.05, min(2.0, d))

    freq_ghz = float(params.get("freq_ghz", 3.0))
    freq_ghz = max(0.1, min(30.0, freq_ghz))

    beta_deg = float(params.get("beta_deg", 0.0))
    beta_rad = np.radians(beta_deg)

    theta0_deg = float(params.get("theta0_deg", 90.0))
    step_deg = float(params.get("angular_step_deg", 0.25))
    step_deg = max(0.05, min(2.0, step_deg))

    w_type = params.get("weighting_type", "Uniform")
    custom_w = params.get("weights", None)

    if w_type == "Custom" and custom_w is not None and len(custom_w) == N:
        weights = np.array(custom_w, dtype=np.float64)
    else:
        weights = get_weights_by_type(w_type, N)

    # Compute grid
    num_pts = max(181, int(round(180.0 / step_deg)) + 1)
    theta_rad = np.linspace(0.0, np.pi, num_pts)
    theta_deg = np.degrees(theta_rad)

    is_uniform = ("uniform" in w_type.lower())
    amplitudes = None if is_uniform else weights

    af_n, p_n, af_db = compute_normalized_pattern(
        theta_rad, N, d, beta_rad, amplitudes=amplitudes
    )

    metrics = compute_pattern_metrics(
        theta_rad, af_n, af_db, N, d, beta_rad,
        selected_steering_theta_deg=theta0_deg,
        is_uniform=is_uniform,
    )

    lam_m = frequency_to_wavelength(freq_ghz * 1e9)
    spacing_mm = physical_spacing_mm(d, freq_ghz * 1e9)
    achieved_rad = compute_achieved_angle(beta_rad, d)
    achieved_deg = float(np.degrees(achieved_rad)) if achieved_rad is not None else None

    return {
        "parameters": {
            "N": N,
            "d_over_lambda": d,
            "freq_ghz": freq_ghz,
            "wavelength_mm": round(lam_m * 1000.0, 2),
            "physical_spacing_mm": round(spacing_mm, 2),
            "beta_deg": beta_deg,
            "theta0_deg": theta0_deg,
            "achieved_beam_deg": achieved_deg,
            "weighting_type": w_type,
            "weights": [round(float(w), 4) for w in weights],
        },
        "metrics": {
            "main_beam_deg": round(metrics.main_beam_deg, 2) if metrics.main_beam_deg is not None else None,
            "hpbw_deg": round(metrics.hpbw_deg, 2) if metrics.hpbw_deg is not None else None,
            "half_power_left_deg": round(metrics.half_power_left_deg, 2) if metrics.half_power_left_deg is not None else None,
            "half_power_right_deg": round(metrics.half_power_right_deg, 2) if metrics.half_power_right_deg is not None else None,
            "fnbw_deg": round(metrics.fnbw_deg, 2) if metrics.fnbw_deg is not None else None,
            "first_null_left_deg": round(metrics.first_null_left_deg, 2) if metrics.first_null_left_deg is not None else None,
            "first_null_right_deg": round(metrics.first_null_right_deg, 2) if metrics.first_null_right_deg is not None else None,
            "peak_sll_db": round(metrics.peak_sll_db, 2) if metrics.peak_sll_db is not None else None,
            "peak_sll_angle_deg": round(metrics.peak_sll_angle_deg, 2) if metrics.peak_sll_angle_deg is not None else None,
            "grating_lobe_count": metrics.grating_lobe_count,
            "grating_lobes_deg": [round(g, 2) for g in metrics.grating_lobes_deg],
            "all_maxima_deg": [round(m, 2) for m in metrics.all_maxima_deg],
            "nulls_deg": [round(n, 2) for n in metrics.nulls_deg],
            "kd_rad": round(metrics.kd_rad, 4),
            "kd_deg": round(metrics.kd_deg, 2),
            "beta_rad": round(metrics.beta_rad, 4),
            "beta_deg": round(metrics.beta_deg, 2),
        },
        "pattern": {
            "theta_deg": [round(float(t), 2) for t in theta_deg],
            "af_normalized": [round(float(a), 5) for a in af_n],
            "af_db": [round(float(b), 2) for b in af_db],
            "power_normalized": [round(float(p), 5) for p in p_n],
        }
    }


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        params = {}
        for k, v in qs.items():
            params[k] = v[0]

        try:
            data = run_simulation(params)
            self._send_json(data, 200)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            params = json.loads(body) if body else {}
            data = run_simulation(params)
            self._send_json(data, 200)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _send_json(self, data: dict, status_code: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
