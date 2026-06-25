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

    t = len(resolution) // 2

    volume = (
        resolution[f"TimePoint {t}"]
        ["Channel 0"]
        ["Data"][:]
    )

print(volume.shape)

n_z = volume.shape[0]

cols = 4
rows = int(np.ceil(n_z / cols))

fig, axes = plt.subplots(
    rows,
    cols,
    figsize=(12, rows * 3)
)

axes = axes.ravel()

for z in range(n_z):

    axes[z].imshow(
        normalize(volume[z]),
        cmap="gray"
    )

    axes[z].set_title(f"Z={z}")

    axes[z].axis("off")
    
# hide unused subplots
for ax in axes[n_z:]:

    ax.axis("off")

plt.tight_layout()

outfile = (
    FIGURES_DIR /
    "zstack_explorer.png"
)

plt.savefig(
    outfile,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {outfile}")
