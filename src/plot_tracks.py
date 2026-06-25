from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent

tracks = pd.read_csv(
    PROJECT_DIR /
    "Analysis" /
    "object_tracks.csv"
)

plt.figure(figsize=(8,8))

for _, row in tracks.iterrows():

    plt.plot(
        [row["x1"], row["x2"]],
        [row["y1"], row["y2"]],
        alpha=0.1
    )

plt.gca().invert_yaxis()

plt.title("Object Motion Vectors")

plt.tight_layout()

plt.savefig(
    PROJECT_DIR /
    "Figures" /
    "object_motion_vectors.png",
    dpi=300
)

plt.show()
