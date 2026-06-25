from pathlib import Path
import h5py
import numpy as np
import imageio.v2 as imageio

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "Data"

MOVIES_DIR = PROJECT_DIR / "Movies"
MOVIES_DIR.mkdir(exist_ok=True)

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

movie_ch0 = []
movie_ch2 = []
movie_overlay = []

with h5py.File(h5_path, "r") as f:

    resolution = f["DataSet"]["ResolutionLevel 0"]

    n_timepoints = len(resolution)

    print(f"Timepoints: {n_timepoints}")

    for t in range(n_timepoints):

        if t % 10 == 0:
            print(f"Processing T={t}")

        ch0 = (
            resolution[f"TimePoint {t}"]
            ["Channel 0"]
            ["Data"][:]
        )

        mip0 = np.max(ch0, axis=0)

        mip0 = normalize(mip0)

        frame0 = (255 * mip0).astype(np.uint8)

        movie_ch0.append(frame0)

        ch2 = (
            resolution[f"TimePoint {t}"]
            ["Channel 2"]
            ["Data"][:]
        )

        mip2 = np.max(ch2, axis=0)

        mip2 = normalize(mip2)

        frame2 = (255 * mip2).astype(np.uint8)

        movie_ch2.append(frame2)

        rgb = np.dstack([
            mip0,              # red
            mip2,              # green
            np.zeros_like(mip0)
        ])

        rgb = (255 * rgb).astype(np.uint8)

        movie_overlay.append(rgb)

print("\nWriting movies...")

imageio.mimsave(
    MOVIES_DIR / "channel0_timelapse.mp4",
    movie_ch0,
    fps=10,
    codec="libx264"
)

imageio.mimsave(
    MOVIES_DIR / "channel2_timelapse.mp4",
    movie_ch2,
    fps=10,
    codec="libx264"
)

imageio.mimsave(
    MOVIES_DIR / "overlay_timelapse.mp4",
    movie_overlay,
    fps=10,
    codec="libx264"
)

print("\nFinished.")
