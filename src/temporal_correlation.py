from pathlib import Path
import h5py
import numpy as np
import matplotlib.pyplot as plt


PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "Data"
FIGURES_DIR = PROJECT_DIR / "Figures"

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

    reference = (
        resolution["TimePoint 0"]
        ["Channel 0"]
        ["Data"][:]
    )

    reference = normalize(reference)

    reference = np.max(reference, axis=0)

    reference = reference.flatten()

    n_timepoints = len(resolution)

    correlations = []

    for t in range(n_timepoints):

        if t % 10 == 0:
            print(f"T={t}")

        volume = (
            resolution[f"TimePoint {t}"]
            ["Channel 0"]
            ["Data"][:]
        )

        volume = normalize(volume)

        mip = np.max(volume, axis=0)

        current = mip.flatten()
# correlation to T0
        corr = np.corrcoef(
            reference,
            current
        )[0,1]

        correlations.append(corr)


plt.figure(figsize=(8,5))

plt.plot(
    correlations,
    linewidth=2
)

plt.xlabel("Timepoint")
plt.ylabel("Correlation to T0")

plt.title("Structural Similarity Relative to T0")

plt.tight_layout()

outfile = (
    FIGURES_DIR /
    "temporal_correlation.png"
)

plt.savefig(
    outfile,
    dpi=300
)

plt.close()

print(f"Saved: {outfile}")
