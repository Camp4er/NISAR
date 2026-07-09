from flask import Flask, render_template, jsonify, request
import numpy as np
import json, base64, math
from pathlib import Path
from datetime import datetime
from qa_engine import get_answer

app = Flask(__name__)

BASE      = Path(r"C:\Users\saxen\OneDrive\Desktop\NISAR_Project")
PROCESSED = BASE / "data" / "processed"
OUTPUTS   = BASE / "outputs"
RAW       = BASE / "data" / "raw"

def load_stats():
    try:
        with open(PROCESSED / "deformation_stats.json") as f:
            return json.load(f)
    except:
        return {}

def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def get_nc_files():
    return sorted(RAW.glob("*.nc"))

def extract_date_from_filename(fname):
    """Extract date from ARIA GUNW filename"""
    parts = fname.stem.split("-")
    for part in parts:
        if len(part) == 17 and "_" in part:
            dates = part.split("_")
            if len(dates) == 2:
                return dates[0], dates[1]
    return None, None

def compute_time_series():
    import h5py
    files = get_nc_files()
    series = []
    for f in files:
        try:
            with h5py.File(f, 'r') as hf:
                found_phase = [None]
                found_coh   = [None]

                def finder(name, obj):
                    if isinstance(obj, h5py.Dataset):
                        if 'unwrappedPhase' in name and found_phase[0] is None:
                            found_phase[0] = name
                        if 'coherence' in name and found_coh[0] is None:
                            found_coh[0] = name

                hf.visititems(finder)

                if found_phase[0] and found_coh[0]:
                    phase = hf[found_phase[0]][:]
                    coh   = hf[found_coh[0]][:]
                    disp  = (phase / (4 * np.pi)) * 0.055465 * 100
                    mask  = coh > 0.5
                    valid = disp[mask]
                    d1, d2 = extract_date_from_filename(f)
                    series.append({
                        "file": f.name[:35] + "...",
                        "date1": d1 or "Unknown",
                        "date2": d2 or "Unknown",
                        "mean_disp": float(np.mean(valid)),
                        "max_uplift": float(np.max(valid)),
                        "max_subsidence": float(np.min(valid)),
                        "std": float(np.std(valid)),
                        "valid_pixels": int(np.sum(mask))
                    })
                else:
                    series.append({"file": f.name[:35], "error": "Layers not found"})
        except Exception as e:
            series.append({"file": f.name[:35], "error": str(e)})
    return series

def compute_risk(series):
    """Compute risk level from time series velocity"""
    if len(series) < 2:
        return {
            "level": "UNKNOWN",
            "color": "gray",
            "score": 0,
            "velocity": 0,
            "message": "Insufficient data for risk assessment",
            "magnitude_estimate": "N/A",
            "affected_population": "N/A"
        }

    valid = [s for s in series if "error" not in s]
    if len(valid) < 2:
        return {"level": "UNKNOWN", "color": "gray", "score": 0,
                "velocity": 0, "message": "Data error", 
                "magnitude_estimate": "N/A", "affected_population": "N/A"}

    # Calculate velocity (change in mean displacement across acquisitions)
    displacements = [s["mean_disp"] for s in valid]
    velocity      = abs(displacements[-1] - displacements[0]) / len(valid)
    std_vals      = [s["std"] for s in valid]
    avg_std       = np.mean(std_vals)

    # Risk scoring
    score = 0
    if abs(velocity) > 2.0:  score += 40
    elif abs(velocity) > 1.0: score += 20
    if avg_std > 5.0:  score += 30
    elif avg_std > 3.0: score += 15
    max_sub = abs(min(s["max_subsidence"] for s in valid))
    if max_sub > 15: score += 30
    elif max_sub > 8: score += 15

    # Magnitude estimate using Wells & Coppersmith
    rupture_area = max(valid[-1]["valid_pixels"] * 0.0001, 100)
    mag_estimate = round(4.07 + 0.98 * math.log10(rupture_area), 1)

    # Population estimate based on magnitude
    if mag_estimate >= 7.0:
        pop = "10–15 million"
    elif mag_estimate >= 6.0:
        pop = "3–5 million"
    else:
        pop = "500K–1 million"

    # Risk level
    if score >= 60:
        level, color = "CRITICAL", "#ff1744"
        msg = (f"CRITICAL: Anomalous deformation velocity detected ({velocity:.2f} cm/acquisition). "
               f"Strain accumulation significantly above baseline. "
               f"Immediate notification of civil authorities recommended.")
    elif score >= 40:
        level, color = "HIGH", "#ff6d00"
        msg = (f"HIGH RISK: Elevated deformation velocity ({velocity:.2f} cm/acquisition) "
               f"detected along the Oldham Fault segment. "
               f"Activate preparedness protocols.")
    elif score >= 20:
        level, color = "ELEVATED", "#ffd600"
        msg = (f"ELEVATED: Deformation rate ({velocity:.2f} cm/acquisition) "
               f"above normal baseline. Increase monitoring frequency.")
    else:
        level, color = "NORMAL", "#00e676"
        msg = (f"NORMAL: Deformation velocity ({velocity:.2f} cm/acquisition) "
               f"within expected baseline range. Continue routine monitoring.")

    return {
        "level": level,
        "color": color,
        "score": score,
        "velocity": round(velocity, 3),
        "message": msg,
        "magnitude_estimate": str(mag_estimate),
        "affected_population": pop,
        "displacements": displacements,
        "std_values": std_vals
    }

# ── Routes ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stats")
def stats():
    return jsonify(load_stats())

@app.route("/api/displacement-map")
def displacement_map():
    return jsonify({"image": image_to_base64(OUTPUTS / "shillong_displacement_map.png")})

@app.route("/api/historical-chart")
def historical_chart():
    return jsonify({"image": image_to_base64(OUTPUTS / "historical_earthquakes.png")})

@app.route("/api/time-series")
def time_series():
    return jsonify(compute_time_series())

@app.route("/api/risk")
def risk():
    series = compute_time_series()
    return jsonify(compute_risk(series))

@app.route("/api/ask", methods=["POST"])
def ask():
    data     = request.get_json()
    question = data.get("question", "")
    answer   = get_answer(question)
    return jsonify({"answer": answer})

@app.route("/api/trigger-alert", methods=["POST"])
def trigger_alert():
    """Demo endpoint to trigger a critical alert"""
    return jsonify({
        "level": "CRITICAL",
        "color": "#ff1744",
        "score": 85,
        "velocity": 4.2,
        "magnitude_estimate": "6.8",
        "affected_population": "3–5 million",
        "message": ("⚠️ CRITICAL ALERT: Rapid surface deformation detected along the Oldham Fault. "
                   "Deformation velocity 4.2 cm/acquisition — 3.1x above baseline. "
                   "Anomalous uplift pattern consistent with pre-seismic strain release. "
                   "Estimated potential magnitude: M6.8. "
                   "Affected population within 100km: 3–5 million. "
                   "RECOMMENDATION: Notify NDMA, State Disaster Management Authorities. "
                   "Activate emergency preparedness protocols for Shillong, Guwahati regions.")
    })

if __name__ == "__main__":
    app.run(debug=True)