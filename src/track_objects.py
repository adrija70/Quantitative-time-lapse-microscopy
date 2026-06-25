from pathlib import Path

import h5py
import pandas as pd
import numpy as np

from skimage.feature import blob_log


PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "Data"
ANALYSIS_DIR = PROJECT_DIR / "Analysis"

ANALYSIS_DIR.mkdir(exist_ok=True)

h5_path = next(DATA_DIR.glob("*.h5"))

records = []

with h5py.File(h5_path, "r") as f:

    res = f["DataSet"]["ResolutionLevel 0"]

    n_timepoints = len(res)

    for t in range(n_timepoints):

        print(f"T={t}")

        img = (
            res[f"TimePoint {t}"]
            ["Channel 0"]
            ["Data"][:]
        )

        mip = np.max(img, axis=0)

        mip = mip.astype(float)

        mip -= mip.min()

        if mip.max() > 0:
            mip /= mip.max()

        blobs = blob_log(
            mip,
            min_sigma=2,
            max_sigma=10,
            num_sigma=10,
            threshold=0.08
        )

        for b in blobs:

            y, x, sigma = b

            records.append([
                t,
                x,
                y,
                sigma
            ])

df = pd.DataFrame(
    records,
    columns=[
        "time",
        "x",
        "y",
        "sigma"
    ]
)

outfile = ANALYSIS_DIR / "detected_objects.csv"

df.to_csv(outfile, index=False)

print()
print("Saved:")
print(outfile)
print()
print("Total detections:", len(df))
