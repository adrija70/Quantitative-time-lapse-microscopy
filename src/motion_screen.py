from pathlib import Path
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "Data"
FIGURES_DIR = PROJECT_DIR / "Figures"
ANALYSIS_DIR = PROJECT_DIR / "Analysis"

FIGURES_DIR.mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(exist_ok=True)


h5_path = next(DATA_DIR.glob("*.h5"))

print(f"Opening {h5_path.name}")


def normalize(img):

    img = img.astype(np.float32)

    p1 = np.percentile(img, 1)
    p99 = np.percentile(img, 99)

    img = np.clip(img, p1, p99)

    img -= img.min()

    if img.max() > 0:
        img /= img.max()

    return img

motion_values = []

with h5py.File(h5_path, "r") as f:

    resolution = f["DataSet"]["ResolutionLevel 0"]

    n_timepoints = len(resolution)

    previous = None

    for t in range(n_timepoints):

        if t % 10 == 0:
            print(f"T={t}")

        volume = (
            resolution[f"TimePoint {t}"]
            ["Channel 0"]
            ["Data"][:]
        )

        mip = np.max(volume, axis=0)

        mip = normalize(mip)

        if previous is not None:
# frame-to-frame difference
            diff = np.abs(mip - previous)

            motion_values.append({
                "timepoint": t,
                "mean_difference": np.mean(diff),
                "max_difference": np.max(diff)
            })

        previous = mip


df = pd.DataFrame(motion_values)

csv_file = ANALYSIS_DIR / "motion_statistics.csv"

df.to_csv(csv_file, index=False)

plt.figure(figsize=(8,5))

plt.plot(
    df["timepoint"],
    df["mean_difference"]
)

plt.xlabel("Timepoint")
plt.ylabel("Mean Frame Difference")
plt.title("Motion Estimate (Channel 0)")

plt.tight_layout()

plot_file = FIGURES_DIR / "mean_motion_vs_time.png"

plt.savefig(
    plot_file,
    dpi=300
)

plt.close()

print(f"Saved: {csv_file}")
print(f"Saved: {plot_file}")

print("Finished.")
