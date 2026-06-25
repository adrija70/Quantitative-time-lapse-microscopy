from pathlib import Path

import h5py
import numpy as np
import matplotlib.pyplot as plt

from skimage.feature import blob_log


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

    midpoint = len(resolution) // 2

    volume = (
        resolution[f"TimePoint {midpoint}"]
        ["Channel 0"]
        ["Data"][:]
    )

mip = np.max(volume, axis=0)

mip = normalize(mip)


blobs = blob_log(
    mip,
    min_sigma=2,
    max_sigma=10,
    num_sigma=10,
    threshold=0.08 # detection threshold
)

print(f"Detected objects: {len(blobs)}")


fig, ax = plt.subplots(figsize=(8,8))

ax.imshow(mip, cmap="gray")

for blob in blobs:

    y, x, r = blob

    circle = plt.Circle(
        (x, y),
        r * np.sqrt(2),
        color="lime",
        fill=False,
        linewidth=1
    )

    ax.add_patch(circle)

ax.set_title(
    f"Detected Objects (n={len(blobs)})"
)

ax.axis("off")

outfile = (
    FIGURES_DIR /
    "object_detection_prototype.png"
)

plt.savefig(
    outfile,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {outfile}")
