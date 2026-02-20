#!/usr/bin/env python3
"""
GENESIS Risk ML Engine v10.1
Predictive risk scoring based on infrastructure metrics.

Features:
- Multi-feature risk prediction (CPU, Memory, Network, Disk, Error Rate)
- Gradient Boosted model for non-linear risk patterns
- Confidence intervals for regulatory reporting
- JSON output for audit trail integration
"""

import json
import sys
from datetime import datetime, timezone

try:
    import numpy as np
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import cross_val_score
except ImportError:
    print("Installing dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                          "numpy", "scikit-learn", "pandas"])
    import numpy as np
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import cross_val_score

TRAINING_DATA = {
    "cpu":        [20, 30, 40, 50, 55, 60, 65, 70, 75, 80, 85, 90, 92, 95, 98],
    "memory":     [15, 25, 30, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95],
    "network_io": [10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 65, 70, 75, 80, 90],
    "disk_usage": [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 92],
    "error_rate": [ 0,  1,  2,  3,  4,  5,  7,  9, 12, 15, 20, 30, 40, 60, 80],
    "risk_score": [ 5,  8, 12, 18, 22, 28, 35, 42, 52, 65, 72, 82, 88, 94, 99],
}

X = np.array([
    TRAINING_DATA["cpu"],
    TRAINING_DATA["memory"],
    TRAINING_DATA["network_io"],
    TRAINING_DATA["disk_usage"],
    TRAINING_DATA["error_rate"],
]).T

y = np.array(TRAINING_DATA["risk_score"])

model = GradientBoostingRegressor(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    random_state=42
)
model.fit(X, y)

cv_scores = cross_val_score(model, X, y, cv=3, scoring="r2")

current_metrics = {
    "cpu": float(sys.argv[1]) if len(sys.argv) > 1 else 75.0,
    "memory": float(sys.argv[2]) if len(sys.argv) > 2 else 65.0,
    "network_io": float(sys.argv[3]) if len(sys.argv) > 3 else 50.0,
    "disk_usage": float(sys.argv[4]) if len(sys.argv) > 4 else 60.0,
    "error_rate": float(sys.argv[5]) if len(sys.argv) > 5 else 12.0,
}

input_vector = np.array([[
    current_metrics["cpu"],
    current_metrics["memory"],
    current_metrics["network_io"],
    current_metrics["disk_usage"],
    current_metrics["error_rate"],
]])

risk_score = float(np.clip(model.predict(input_vector)[0], 0, 100))

feature_importance = dict(zip(
    ["cpu", "memory", "network_io", "disk_usage", "error_rate"],
    [round(float(x), 4) for x in model.feature_importances_]
))

if risk_score >= 80:
    risk_level = "CRITICAL"
elif risk_score >= 60:
    risk_level = "HIGH"
elif risk_score >= 40:
    risk_level = "MEDIUM"
elif risk_score >= 20:
    risk_level = "LOW"
else:
    risk_level = "MINIMAL"

result = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "version": "10.1.0",
    "engine": "GradientBoostingRegressor",
    "input_metrics": current_metrics,
    "risk_score": round(risk_score, 2),
    "risk_level": risk_level,
    "confidence": {
        "cv_r2_mean": round(float(cv_scores.mean()), 4),
        "cv_r2_std": round(float(cv_scores.std()), 4),
    },
    "feature_importance": feature_importance,
    "model_params": {
        "n_estimators": 100,
        "max_depth": 4,
        "training_samples": len(y),
    },
    "recommendation": (
        "IMMEDIATE ACTION REQUIRED" if risk_level == "CRITICAL" else
        "Escalate to operations team" if risk_level == "HIGH" else
        "Monitor closely" if risk_level == "MEDIUM" else
        "Normal operations"
    ),
}

with open("risk_score.json", "w") as f:
    json.dump(result, f, indent=2)

with open("risk_score.txt", "w") as f:
    f.write(str(round(risk_score)))

print(json.dumps(result, indent=2))
