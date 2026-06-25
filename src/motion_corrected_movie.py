from pathlib import Path

import h5py
import numpy as np
import imageio.v2 as imageio

import matplotlib.pyplot as plt

from scipy.ndimage import shift
from skimage.registration import phase_cross_correlation


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


def create_overlay(ch0, ch1, ch2):

    rgb = np.zeros(
        (*ch0.shape, 3),
        dtype=np.float32
    )
# R=ch0, G=ch2, B=ch1
    rgb[..., 0] = normalize(ch0)   # red
    rgb[..., 1] = normalize(ch2)   # green
    rgb[..., 2] = normalize(ch1)   # blue

    rgb = (rgb * 255).astype(np.uint8)

    return rgb


with h5py.File(h5_path, "r") as f:

    resolution = f["DataSet"]["ResolutionLevel 0"]

    n_timepoints = len(resolution)

    ref_vol = (
        resolution["TimePoint 0"]
        ["Channel 0"]
        ["Data"][:]
    )

    ref_mip = normalize(
        np.max(ref_vol, axis=0)
    )

    shifts_x = []
    shifts_y = []

    raw_frames = []
    corrected_frames = []

    for t in range(n_timepoints):

        if t % 10 == 0:
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

        mip0 = normalize(np.max(ch0, axis=0))

      
# estimate drift relative to T0
        drift, error, _ = phase_cross_correlation(
            ref_mip,
            mip0,
            upsample_factor=10
        )

        y_shift, x_shift = drift

        shifts_x.append(x_shift)
        shifts_y.append(y_shift)

    

        raw_overlay = create_overlay(
            np.max(ch0, axis=0),
            np.max(ch1, axis=0),
            np.max(ch2, axis=0)
        )

       
# apply drift correction
        ch0_corr = shift(
            np.max(ch0, axis=0),
            shift=(-y_shift, -x_shift),
            order=1
        )

        ch1_corr = shift(
            np.max(ch1, axis=0),
            shift=(-y_shift, -x_shift),
            order=1
        )

        ch2_corr = shift(
            np.max(ch2, axis=0),
            shift=(-y_shift, -x_shift),
            order=1
        )

        corr_overlay = create_overlay(
            ch0_corr,
            ch1_corr,
            ch2_corr
        )


        combined = np.concatenate(
            [raw_overlay, corr_overlay],
            axis=1
        )

        raw_frames.append(raw_overlay)
        corrected_frames.append(combined)

plt.figure(figsize=(8,5))

plt.plot(shifts_x, label="X shift")
plt.plot(shifts_y, label="Y shift")

plt.xlabel("Timepoint")
plt.ylabel("Pixels")

plt.title("Estimated Drift")

plt.legend()

plt.tight_layout()

plt.savefig(
    FIGURES_DIR /
    "motion_correction_drift.png",
    dpi=300
)

plt.close()


for idx in [0, 60, 119]:

    plt.figure(figsize=(10,5))

    plt.imshow(corrected_frames[idx])

    plt.axis("off")

    plt.title(
        f"Raw (left) vs Corrected (right) T={idx}"
    )

    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR /
        f"motion_compare_t{idx:03d}.png",
        dpi=300
    )

    plt.close()


print("Writing GIF...")

imageio.mimsave(
    FIGURES_DIR /
    "motion_corrected_comparison.gif",
    corrected_frames,
    duration=0.1
)

print("Finished.")
