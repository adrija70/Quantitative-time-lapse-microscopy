from pathlib import Path
import h5py
import numpy as np
import matplotlib.pyplot as plt


PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "Data"
FIGURES_DIR = PROJECT_DIR / "Figures"
ANALYSIS_DIR = PROJECT_DIR / "Analysis"
# MIP output folder
MIP_DIR = FIGURES_DIR / "MIPs"
MIP_DIR.mkdir(parents=True, exist_ok=True)

h5_path = next(DATA_DIR.glob("*.h5"))

print(f"\nOpening: {h5_path.name}")

# Contrast normalization for display
def normalize_image(img):
    img = img.astype(np.float32)

    p1 = np.percentile(img, 1)
    p99 = np.percentile(img, 99)

    img = np.clip(img, p1, p99)

    img = (img - img.min()) / (img.max() - img.min() + 1e-8)

    return img

with h5py.File(h5_path, "r") as f:

    resolution = f["DataSet"]["ResolutionLevel 0"]

    n_timepoints = len(resolution)

    n_channels = len(
        resolution["TimePoint 0"]
    )

    print(f"Timepoints: {n_timepoints}")
    print(f"Channels: {n_channels}")

 # First, middle and last timepoints
    representative_times = [
        0,
        n_timepoints // 2,
        n_timepoints - 1
    ]

    summary = []

    for t in representative_times:

        print(f"\nProcessing T={t}")

        fig, axes = plt.subplots(
            1,
            n_channels,
            figsize=(5 * n_channels, 5)
        )

        if n_channels == 1:
            axes = [axes]

        for ch in range(n_channels):

            volume = (
                resolution[f"TimePoint {t}"]
                [f"Channel {ch}"]
                ["Data"][:]
            )

            mip = np.max(volume, axis=0)

            summary.append(
                f"T={t}, CH={ch}, "
                f"mean={mip.mean():.2f}, "
                f"max={mip.max():.2f}"
            )

            axes[ch].imshow(
                normalize_image(mip),
                cmap="gray"
            )

            axes[ch].set_title(
                f"T{t} CH{ch}"
            )

            axes[ch].axis("off")

        plt.tight_layout()

        out_file = (
            MIP_DIR /
            f"mip_t{t:03d}.png"
        )

        plt.savefig(
            out_file,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(f"Saved: {out_file.name}")

metrics_file = (
    ANALYSIS_DIR /
    "mip_summary.txt"
)

with open(metrics_file, "w") as f:
    f.write("\n".join(summary))

print("\nFinished.")
