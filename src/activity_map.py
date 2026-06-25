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

# accumulate frame-to-frame change
activity_map = None
previous = None

with h5py.File(h5_path, "r") as f:

    resolution = f["DataSet"]["ResolutionLevel 0"]

    n_timepoints = len(resolution)

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

            diff = np.abs(mip - previous)

            if activity_map is None:
                activity_map = diff
            else:
                activity_map += diff

        previous = mip


plt.figure(figsize=(8,8))

plt.imshow(
    activity_map,
    cmap="hot"
)

plt.colorbar(label="Accumulated Change")

plt.title(
    "Activity Map (Channel 0)"
)

plt.axis("off")

outfile = (
    FIGURES_DIR /
    "activity_map.png"
)

plt.savefig(
    outfile,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {outfile}")

print("Finished.")
