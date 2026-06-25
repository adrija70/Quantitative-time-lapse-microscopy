from pathlib import Path
import h5py
import numpy as np
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "Data"
FIGURES_DIR = PROJECT_DIR / "Figures"

OVERLAY_DIR = FIGURES_DIR / "Overlays"
OVERLAY_DIR.mkdir(parents=True, exist_ok=True)


h5_path = next(DATA_DIR.glob("*.h5"))

print(f"\nOpening: {h5_path.name}")


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

    n_timepoints = len(resolution)

    representative_times = [
        0,
        n_timepoints // 2,
        n_timepoints - 1
    ]

    for t in representative_times:

        print(f"Processing T={t}")

        ch0 = (
            resolution[f"TimePoint {t}"]
            ["Channel 0"]
            ["Data"][:]
        )

        ch1 = (
            resolution[f"TimePoint {t}"]
            ["Channel 1"]
            ["Data"][:]
        )

        ch2 = (
            resolution[f"TimePoint {t}"]
            ["Channel 2"]
            ["Data"][:]
        )

        mip0 = np.max(ch0, axis=0)
        mip1 = np.max(ch1, axis=0)
        mip2 = np.max(ch2, axis=0)

        mip0 = normalize(mip0)
        mip1 = normalize(mip1)
        mip2 = normalize(mip2)

        # RGB Overlay
        rgb = np.dstack([
            mip0,   # Red
            mip2,   # Green
            mip1    # Blue
        ])  # R=ch0, G=ch2, B=ch1

        plt.figure(figsize=(8, 8))
        plt.imshow(rgb)
        plt.title(f"Overlay T={t}")
        plt.axis("off")

        outfile = OVERLAY_DIR / f"overlay_t{t:03d}.png"

        plt.savefig(
            outfile,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(f"Saved: {outfile.name}")

print("\nFinished.")
