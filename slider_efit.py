import numpy as np
from matplotlib import pyplot as plt, cm
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib import gridspec
import pdb
import sys
from PyQt5.QtCore import pyqtRemoveInputHook
from netCDF4 import Dataset


# def pyqt_set_trace():
#     """Set a tracepoint in the Python debugger that works with Qt"""

#     pyqtRemoveInputHook()
#     # pdb.set_trace()
#     # set up the debugger
#     debugger = pdb.Pdb()
#     debugger.reset()
#     # custom next to get outside of function scope
#     debugger.do_next(None)  # run the next command
#     users_frame = (
#         sys._getframe().f_back
#     )  # frame where the user invoked `pyqt_set_trace()`
#     debugger.interaction(users_frame, None)


def exes(mn, mx, scale=0.02):
    "expand axes by scale"
    r = (mx - mn) * scale
    return mn - r, mx + r


def lexes(mn, mx, scale=0.02):
    "expand log axes by scale"
    assert mn > 0
    assert mx > 0
    r = (mx / mn) ** scale
    return mn / r, mx * r


ds = Dataset("data/97708_efitOut.nc")
ds["/output"].groups.values()


# In[6]:


time = ds["time"][:]

# vessel outline
r_limit = ds["/input/limiter/rValues"][:]
z_limit = ds["/input/limiter/zValues"][:]

# load up constraints
magnetic_probes = ds["/input/constraints/magneticProbes"]
num_probes = magnetic_probes.dimensions["magneticProbeDim"].size

# where are the probes located around the vessel
rc = magnetic_probes["rCentre"][:]
zc = magnetic_probes["zCentre"][:]
po = magnetic_probes["poloidalOrientation"][:]

# recorded signal
targ = magnetic_probes["target"][:]
sigma = magnetic_probes["sigmas"][:]
weight = magnetic_probes["weights"][:]
comp = magnetic_probes["computed"][:]

# where is the output sampled
r_grid = ds["/output/profiles2D/r"][:]
z_grid = ds["/output/profiles2D/z"][:]

# LCMS
geometry_boundary = ds["/output/separatrixGeometry/boundaryCoords"][:]

# import pdb

# pdb.set_trace()
poloidal_flux = ds["/output/profiles2D/poloidalFlux"][:]

axis_color = "lightgoldenrodyellow"

td = np.empty((len(time), 2, 2))
td[:, 0, 0] = time
td[:, 1, 0] = time

fig = plt.figure(figsize=(20, 15))
# heights1 = [3, 3]
# gs = gridspec.GridSpec(ncols=1, nrows=5, height_ratios=heights1)
gs = fig.add_gridspec(6, 6)

ax_2d = fig.add_subplot(gs[0:5, 0:2])
# ax_2d.set_xlim(left, right)
ax_time = fig.add_subplot(gs[0:5, 2:6])
ax_chi2 = fig.add_subplot(gs[0:3, 2:6], sharex=ax_time)
ax_chi2.tick_params("x", labelbottom=False)

chi2 = ((comp - targ) * weight / sigma) ** 2
chi2s = np.sum(chi2, axis=0)

ccm = cm.viridis(chi2s / max(chi2s))
ccm[:, 3] = 0.1 + np.mean(weight > 0, axis=0) * 0.9
ccs = np.ones(num_probes) * 20

ax_2d.contourf(r_grid[0, :], z_grid[0, :], poloidal_flux[0, :, :].T, 21)
ax_2d.plot(r_limit, z_limit, color="lightgray", linewidth=1)
(lc_gb,) = ax_2d.plot([], [])

input_points = ax_2d.scatter(rc, zc, s=ccs, facecolor=ccm, edgecolor="none")
ax_2d.axis("equal")

axt = ax_time.vlines([], [], [], label="$2\sigma$ around constraint")
(axc,) = ax_time.plot([], [], color="k", linewidth=1, label="computed value")
ax_time.legend(loc="lower left")
ax_time.set_xlim(exes(min(time), max(time)))
ax_time.set_ylim(exes(-0.5, 0.5))
ax_time.set_xlabel("time")
l2d_t = ax_time.axvline(np.nan, color="lightgray", linewidth=1)

chi_tr = exes(min(time), max(time))
chi_mn, chi_mx = lexes(0.1, 100)

ax_chi2.fill_between(chi_tr, 0, 1, color="lightgreen", alpha=0.2)
chi_pc = ax_chi2.scatter([], [])
use = weight[:, 1] != 0
chi_pc.set_offsets(np.array([time, np.clip(chi2[:, 1], chi_mn, chi_mx)]).T[use])
comp = magnetic_probes["computed"][:, 1]
axc.set_data(time, comp)
axt.set_segments(td[use])

ax_chi2.semilogy()
ax_chi2.set_xlim(chi_tr)
ax_chi2.set_ylim(chi_mn, chi_mx)


time_slider_ax = fig.add_axes([0.25, 0.07, 0.65, 0.03], facecolor=axis_color)
time_slider = Slider(
    time_slider_ax, "Time", min(time), max(time), valinit=time[0], valstep=time
)


# Draw another slider
probe_slider_ax = fig.add_axes([0.25, 0.02, 0.65, 0.03], facecolor=axis_color)
probe_slider = Slider(
    probe_slider_ax,
    "ProbeID",
    1,
    num_probes - 1,
    valinit=1,
    valstep=range(1, num_probes),
)


def time_sliders_on_changed(value):

    idx = (np.abs(time - value)).argmin()
    c0 = ax_2d.collections[-1]
    ax_2d.collections.clear()

    ax_2d.contourf(r_grid[idx, :], z_grid[idx, :], poloidal_flux[idx, :, :].T, 21)

    fig.canvas.draw_idle()
    # put the probes back in again
    ax_2d.collections.append(c0)

    lc_gb.set_data(geometry_boundary[idx, :]["R"], geometry_boundary[idx, :]["Z"])

    l2d_t.set_data([time[idx], time[idx]], [0, 1])


def probe_sliders_on_changed(pid):
    c = ccm.copy()
    c[pid, :] = [0.9, 0.3, 0.5, 1]
    input_points.set_facecolor(c)

    s = ccs.copy()
    s[pid] = 100
    input_points.set_sizes(s)

    tar = targ[:, pid]
    sig = sigma[:, pid]

    td[:, 0, 1] = tar - 2 * sig
    td[:, 1, 1] = tar + 2 * sig

    use = weight[:, pid] != 0
    axt.set_segments(td[use])

    comp = magnetic_probes["computed"][:, pid]
    axc.set_data(time, comp)

    chi_pc.set_offsets(np.array([time, np.clip(chi2[:, pid], chi_mn, chi_mx)]).T[use])


time_slider.on_changed(time_sliders_on_changed)
probe_slider.on_changed(probe_sliders_on_changed)

ax_reset = plt.axes([0.01, 0.025, 0.1, 0.04])
button = Button(ax_reset, "Reset", hovercolor="0.975")


def reset(event):
    time_slider.reset()
    probe_slider.reset()


button.on_clicked(reset)
# fig.tight_layout(pad=0.2)
plt.show()
# %%
