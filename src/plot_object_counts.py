from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent

csv_path = (
    PROJECT_DIR /
    "Analysis" /
    "detected_objects.csv"
)

df = pd.read_csv(csv_path)

counts = (
    df.groupby("time")
      .size()
)

plt.figure(figsize=(8,5))

plt.plot(counts.index,
         counts.values,
         lw=2)

plt.xlabel("Timepoint")
plt.ylabel("Detected objects")

plt.title("Object Counts vs Time")

plt.tight_layout()

plt.savefig(
    PROJECT_DIR /
    "Figures" /
    "object_counts_vs_time.png",
    dpi=300
)

plt.show()
