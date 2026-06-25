from pathlib import Path
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "Data"
ANALYSIS_DIR = PROJECT_DIR / "Analysis"
FIGURES_DIR = PROJECT_DIR / "Figures"

ANALYSIS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

h5_path = next(DATA_DIR.glob("*.h5"))

print(f"\nOpening: {h5_path.name}")

results = []


with h5py.File(h5_path, "r") as f:

    resolution = f["DataSet"]["ResolutionLevel 0"]

    n_timepoints = len(resolution)

    n_channels = len(
        resolution["TimePoint 0"]
    )

    print(f"Timepoints: {n_timepoints}")
    print(f"Channels: {n_channels}")

    for t in range(n_timepoints):

        if t % 10 == 0:
            print(f"Processing T={t}")

        for ch in range(n_channels):

            volume = (
                resolution[f"TimePoint {t}"]
                [f"Channel {ch}"]
                ["Data"][:]
            )
            
# volume statistics
            results.append({
                "timepoint": t,
                "channel": ch,
                "mean_intensity": np.mean(volume),
                "median_intensity": np.median(volume),
                "max_intensity": np.max(volume),
                "std_intensity": np.std(volume),
                "nonzero_pixels": np.count_nonzero(volume)
            })


df = pd.DataFrame(results)

csv_file = ANALYSIS_DIR / "intensity_statistics.csv"

df.to_csv(csv_file, index=False)

print(f"\nSaved: {csv_file}")


for ch in sorted(df["channel"].unique()):

    sub = df[df["channel"] == ch]

    plt.figure(figsize=(8, 5))

    plt.plot(
        sub["timepoint"],
        sub["mean_intensity"]
    )

    plt.xlabel("Timepoint")
    plt.ylabel("Mean Intensity")
    plt.title(f"Channel {ch}: Mean Intensity vs Time")

    plt.tight_layout()

    out_file = (
        FIGURES_DIR /
        f"channel_{ch}_intensity_vs_time.png"
    )

    plt.savefig(
        out_file,
        dpi=300
    )

    plt.close()

    print(f"Saved: {out_file.name}")

summary_lines = []

for ch in sorted(df["channel"].unique()):

    sub = df[df["channel"] == ch]

    summary_lines.append(
        f"\nCHANNEL {ch}"
    )

    summary_lines.append(
        f"Mean intensity range: "
        f"{sub['mean_intensity'].min():.2f} - "
        f"{sub['mean_intensity'].max():.2f}"
    )

    summary_lines.append(
        f"Max intensity range: "
        f"{sub['max_intensity'].min():.2f} - "
        f"{sub['max_intensity'].max():.2f}"
    )

summary_file = (
    ANALYSIS_DIR /
    "intensity_summary.txt"
)

with open(summary_file, "w") as f:
    f.write("\n".join(summary_lines))

print(f"Saved: {summary_file}")

print("\nFinished.")
