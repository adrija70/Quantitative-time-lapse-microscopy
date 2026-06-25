import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr


H5_FILE = "Data/den1.h5"

print("Opening:", H5_FILE)

with h5py.File(H5_FILE, "r") as f:

    ch0 = []
    ch1 = []
    ch2 = []

    for t in range(120):

        ch0.append(
            np.max(
                f[f"DataSet/ResolutionLevel 0/TimePoint {t}/Channel 0/Data"][:],
                axis=0
            )
        )

        ch1.append(
            np.max(
                f[f"DataSet/ResolutionLevel 0/TimePoint {t}/Channel 1/Data"][:],
                axis=0
            )
        )

        ch2.append(
            np.max(
                f[f"DataSet/ResolutionLevel 0/TimePoint {t}/Channel 2/Data"][:],
                axis=0
            )
        )

ch0 = np.array(ch0)
ch1 = np.array(ch1)
ch2 = np.array(ch2)

print("Loaded.")
print("Shape:", ch0.shape)

# cumulative activity over time
activity_map = np.sum(
    np.abs(np.diff(ch0.astype(float), axis=0)),
    axis=0
)


delta_ch1 = ch1[-1].astype(float) - ch1[0].astype(float)
delta_ch2 = ch2[-1].astype(float) - ch2[0].astype(float)

a = activity_map.ravel()
# change from first to last frame
d1 = delta_ch1.ravel()
d2 = delta_ch2.ravel()

mask1 = np.isfinite(a) & np.isfinite(d1)
mask2 = np.isfinite(a) & np.isfinite(d2)

r1, p1 = pearsonr(a[mask1], d1[mask1])
r2, p2 = pearsonr(a[mask2], d2[mask2])

print("\n========== RESULTS ==========")
print(f"Channel0 Activity vs Channel1 Change")
print(f"r = {r1:.4f}")
print(f"p = {p1:.4e}")

print()

print(f"Channel0 Activity vs Channel2 Change")
print(f"r = {r2:.4f}")
print(f"p = {p2:.4e}")

# top 10% most active pixels
threshold = np.percentile(activity_map, 90)

hotspot = activity_map >= threshold
background = activity_map < threshold

hot_ch1 = np.mean(delta_ch1[hotspot])
bg_ch1 = np.mean(delta_ch1[background])

hot_ch2 = np.mean(delta_ch2[hotspot])
bg_ch2 = np.mean(delta_ch2[background])

print("\n========== HOTSPOTS ==========")

print(f"Channel1 Δ intensity")
print(f"Hotspots     : {hot_ch1:.3f}")
print(f"Background   : {bg_ch1:.3f}")

print()

print(f"Channel2 Δ intensity")
print(f"Hotspots     : {hot_ch2:.3f}")
print(f"Background   : {bg_ch2:.3f}")

fig, ax = plt.subplots(1, 3, figsize=(18, 6))

im0 = ax[0].imshow(activity_map, cmap="hot")
ax[0].set_title("Channel 0 Activity")
ax[0].axis("off")
plt.colorbar(im0, ax=ax[0])

im1 = ax[1].imshow(delta_ch1, cmap="coolwarm")
ax[1].set_title("Δ Channel 1")
ax[1].axis("off")
plt.colorbar(im1, ax=ax[1])

im2 = ax[2].imshow(delta_ch2, cmap="coolwarm")
ax[2].set_title("Δ Channel 2")
ax[2].axis("off")
plt.colorbar(im2, ax=ax[2])

plt.tight_layout()
plt.savefig(
    "channel_interaction_maps.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


sample = np.random.choice(
    len(a),
    size=min(30000, len(a)),
    replace=False
)

fig, ax = plt.subplots(1, 2, figsize=(12, 5))

ax[0].scatter(
    a[sample],
    d1[sample],
    s=1,
    alpha=0.2
)

ax[0].set_title(
    f"Activity vs ΔCh1\nr={r1:.3f}"
)

ax[0].set_xlabel("Activity")
ax[0].set_ylabel("ΔCh1")

ax[1].scatter(
    a[sample],
    d2[sample],
    s=1,
    alpha=0.2
)

ax[1].set_title(
    f"Activity vs ΔCh2\nr={r2:.3f}"
)

ax[1].set_xlabel("Activity")
ax[1].set_ylabel("ΔCh2")

plt.tight_layout()

plt.savefig(
    "channel_correlations.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nFinished.")
