from pathlib import Path
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "Data"
FIGURES_DIR = PROJECT_DIR / "Figures"
ANALYSIS_DIR = PROJECT_DIR / "Analysis"


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

with h5py.File(h5_path, "r") as f:

    resolution = f["DataSet"]["ResolutionLevel 0"]

    first = (
        resolution["TimePoint 0"]
        ["Channel 0"]
        ["Data"][:]
    )

    n_z = first.shape[0]

    activity_per_z = np.zeros(n_z)

    previous = None

    n_timepoints = len(resolution)

    for t in range(n_timepoints):

        if t % 10 == 0:
            print(f"T={t}")

        volume = (
            resolution[f"TimePoint {t}"]
            ["Channel 0"]
            ["Data"][:]
        )

        volume = normalize(volume)

        if previous is not None:

            diff = np.abs(volume - previous)

            for z in range(n_z):
# accumulate activity by z slice

                activity_per_z[z] += diff[z].mean()

        previous = volume


df = pd.DataFrame({
    "z_slice": np.arange(n_z),
    "activity": activity_per_z
})

csv_file = (
    ANALYSIS_DIR /
    "z_activity_profile.csv"
)

df.to_csv(csv_file, index=False)

plt.figure(figsize=(8,5))

plt.plot(
    df["z_slice"],
    df["activity"],
    marker="o"
)

plt.xlabel("Z slice")
plt.ylabel("Accumulated Activity")

plt.title(
    "Motion / Activity vs Z Depth"
)

plt.tight_layout()

outfile = (
    FIGURES_DIR /
    "z_activity_profile.png"
)

plt.savefig(
    outfile,
    dpi=300
)

plt.close()

print(f"Saved: {outfile}")
