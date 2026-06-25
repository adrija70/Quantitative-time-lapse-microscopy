from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.spatial import cKDTree

PROJECT_DIR = Path(__file__).resolve().parent.parent

ANALYSIS_DIR = PROJECT_DIR / "Analysis"
FIGURES_DIR = PROJECT_DIR / "Figures"

FIGURES_DIR.mkdir(exist_ok=True)

df = pd.read_csv(
    ANALYSIS_DIR / "detected_objects.csv"
)

tracks = []

max_link_distance = 20

for t in range(df["time"].max()):

    current = df[df["time"] == t]
    nxt = df[df["time"] == t + 1]

    if len(current) == 0 or len(nxt) == 0:
        continue

    tree = cKDTree(
        nxt[["x", "y"]].values
    )

    distances, indices = tree.query(
        current[["x", "y"]].values,
        distance_upper_bound=max_link_distance
    )

    valid = np.isfinite(distances)

    linked = pd.DataFrame({
        "time": t,
        "x1": current["x"].values[valid],
        "y1": current["y"].values[valid],
        "x2": nxt.iloc[
            indices[valid]
        ]["x"].values,
        "y2": nxt.iloc[
            indices[valid]
        ]["y"].values,
        "distance": distances[valid]
    })

    tracks.append(linked)

tracks = pd.concat(tracks)

tracks.to_csv(
    ANALYSIS_DIR / "object_tracks.csv",
    index=False
)

print("Links:", len(tracks))

plt.figure(figsize=(8,5))

mean_motion = (
    tracks.groupby("time")
          ["distance"]
          .mean()
)

plt.plot(
    mean_motion.index,
    mean_motion.values,
    lw=2
)

plt.xlabel("Timepoint")
plt.ylabel("Mean displacement (pixels)")
plt.title("Object Motion vs Time")

plt.tight_layout()

plt.savefig(
    FIGURES_DIR /
    "object_motion_vs_time.png",
    dpi=300
)

plt.show()
