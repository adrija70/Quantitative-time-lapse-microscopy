from pathlib import Path
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from skimage.registration import phase_cross_correlation

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "Data"
ANALYSIS_DIR = PROJECT_DIR / "Analysis"
FIGURES_DIR = PROJECT_DIR / "Figures"

h5_path = next(DATA_DIR.glob("*.h5"))

print(f"\nOpening {h5_path.name}")

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

    reference = (
        resolution["TimePoint 0"]
        ["Channel 0"]
        ["Data"][:]
    )

    reference = np.max(reference, axis=0)
    reference = normalize(reference)

    results = []

    n_timepoints = len(resolution)

    for t in range(1, n_timepoints):

        if t % 10 == 0:
            print(f"T={t}")

        volume = (
            resolution[f"TimePoint {t}"]
            ["Channel 0"]
            ["Data"][:]
        )

        frame = np.max(volume, axis=0)
        frame = normalize(frame)
        
# estimate drift relative to T0
        shift, error, _ = phase_cross_correlation(
            reference,
            frame,
            upsample_factor=10
        )

        results.append({
            "timepoint": t,
            "shift_y": shift[0],
            "shift_x": shift[1],
            "error": error
        })

df = pd.DataFrame(results)

csv_file = ANALYSIS_DIR / "registration_statistics.csv"

df.to_csv(csv_file, index=False)


plt.figure(figsize=(10,5))

plt.plot(
    df["timepoint"],
    df["shift_x"],
    label="X shift"
)

plt.plot(
    df["timepoint"],
    df["shift_y"],
    label="Y shift"
)

plt.axhline(
    0,
    linestyle="--"
)

plt.xlabel("Timepoint")
plt.ylabel("Pixels")
plt.title("Estimated Drift Relative to T0")

plt.legend()

plt.tight_layout()

plot_file = FIGURES_DIR / "estimated_drift.png"

plt.savefig(
    plot_file,
    dpi=300
)

plt.close()

print(f"Saved: {csv_file}")
print(f"Saved: {plot_file}")

print("\nFinished.")
