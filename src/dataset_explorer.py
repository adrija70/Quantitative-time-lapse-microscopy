from pathlib import Path
import h5py
import numpy as np
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "Data"
ANALYSIS_DIR = PROJECT_DIR / "Analysis"
FIGURES_DIR = PROJECT_DIR / "Figures"

ANALYSIS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

# Assume the first .h5 file in Data is the dataset to analyze
h5_files = list(DATA_DIR.glob("*.h5"))

if len(h5_files) == 0:
    raise FileNotFoundError(
        f"No .h5 file found in {DATA_DIR}"
    )

h5_path = h5_files[0]

print(f"\nOpening file:")
print(h5_path)

# Collect the complete HDF5 hierarchy for later inspection
tree_lines = []

def save_tree(name, obj):
    tree_lines.append(
        f"{name} | {type(obj).__name__}"
    )

with h5py.File(h5_path, "r") as f:

    f.visititems(save_tree)

  
 # Save hierarchy
    structure_file = (
        ANALYSIS_DIR /
        "file_structure.txt"
    )

    with open(structure_file, "w") as out:
        out.write(
            "\n".join(tree_lines)
        )

    print(
        f"Saved: {structure_file.name}"
    )

    summary = []

    summary.append(
        f"File: {h5_path.name}"
    )

    summary.append("\nTop-level groups:")

    for key in f.keys():
        summary.append(key)

   
    # Expected Imaris structure
    try:

        dataset = (
            f["DataSet"]
            ["ResolutionLevel 0"]
            ["TimePoint 0"]
            ["Channel 0"]
            ["Data"]
        )

        z, y, x = dataset.shape

        n_timepoints = len(
            f["DataSet"]
            ["ResolutionLevel 0"]
        )

        n_channels = len(
            f["DataSet"]
            ["ResolutionLevel 0"]
            ["TimePoint 0"]
        )

        summary.append(
            "\nDataset dimensions:"
        )

        summary.append(
            f"Timepoints: {n_timepoints}"
        )

        summary.append(
            f"Channels: {n_channels}"
        )

        summary.append(
            f"Z slices: {z}"
        )

        summary.append(
            f"Image size: {y} x {x}"
        )

        summary.append(
            f"Datatype: {dataset.dtype}"
        )

        # Representative images
                fig, axes = plt.subplots(
            1,
            n_channels,
            figsize=(5*n_channels, 5)
        )

        if n_channels == 1:
            axes = [axes]

        for ch in range(n_channels):

            volume = (
                f["DataSet"]
                ["ResolutionLevel 0"]
                ["TimePoint 0"]
                [f"Channel {ch}"]
                ["Data"][:]
            )

            middle_slice = volume[
                volume.shape[0] // 2
            ]

            axes[ch].imshow(
                middle_slice,
                cmap="gray"
            )

            axes[ch].set_title(
                f"Channel {ch}"
            )

            axes[ch].axis("off")

        plt.tight_layout()

        figure_path = (
            FIGURES_DIR /
            "representative_channels.png"
        )

        plt.savefig(
            figure_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(
            "Saved: representative_channels.png"
        )

    except Exception as e:

        summary.append(
            "\nAutomatic parsing failed:"
        )

        summary.append(str(e))

        print(
            "\nAutomatic parsing failed."
        )

        print(e)

    summary_file = (
        ANALYSIS_DIR /
        "dataset_summary.txt"
    )

    with open(summary_file, "w") as out:
        out.write(
            "\n".join(summary)
        )

    print(
        f"Saved: {summary_file.nam"
    )
e}
print("\nFinished.")
