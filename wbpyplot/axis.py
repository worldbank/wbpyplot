import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
import matplotlib.ticker as mticker 
import numpy as np


def apply_axis_styling(ax, wb_font_sizes, wb_spacing, chart_type):
    # --- shared axis label + tick styling ---
    for axis in [ax.xaxis, ax.yaxis]:
        axis.label.set_fontsize(wb_font_sizes["s"])
        axis.label.set_fontweight("semibold")
        axis.label.set_color("#111111")
        axis.label.set_linespacing(1.2)

    for ticklabel in ax.get_xticklabels() + ax.get_yticklabels():
        ticklabel.set_fontsize(wb_font_sizes["s"])
        ticklabel.set_fontweight("regular")
        ticklabel.set_color("#666666")
        ticklabel.set_linespacing(1.2)

    ax.grid(True, which="major", linestyle=(0, (4, 2)), linewidth=1, color="#CED4DE")
    ax.tick_params(axis="y", which="both", length=0)

    def add_zero_line_h():  # horizontal line at y=0
        if ax.get_yscale() == "linear":
            ax.figure.canvas.draw()
            y0, y1 = ax.get_ylim()
            if y0 <= 0 <= y1:
                ax.axhline(0, linewidth=1, color="#8A969F", zorder=5)

    def add_zero_line_v():  # vertical line at x=0
        if ax.get_xscale() == "linear":
            ax.figure.canvas.draw()
            x0, x1 = ax.get_xlim()
            if x0 <= 0 <= x1:
                ax.axvline(0, linewidth=1, color="#8A969F", zorder=5)

    if chart_type in ("scatter", "bar", "line"):
        add_zero_line_h()
    if chart_type in ["line", "timeseries"]:
        ax.set_ylim(bottom=0)
        add_zero_line_h()

    if chart_type == "scatter":
        x_pad = wb_spacing["xxs"]
        y_pad = wb_spacing["xxs"]
        ax.xaxis.labelpad = x_pad
        ax.yaxis.labelpad = y_pad
        for label in ax.get_xticklabels():
            label.set_y(label.get_position()[1] - 0.01)
        for label in ax.get_yticklabels():
            label.set_x(label.get_position()[0] - 0.01)
        ax.tick_params(axis="y", which="both", length=0)
        ax.tick_params(axis="x", which="both", length=0.1, color="#CED4DE")

    elif chart_type == "timeseries":
        ax.set_xlabel("")
        ax.set_xticks([])
        ax.grid(False, axis="x")
        ax.grid(True, axis="y")

    elif chart_type == "line":
        ax.set_xlabel("")
        for label in ax.get_xticklabels():
            label.set_y(label.get_position()[1] - 0.01)
        for label in ax.get_yticklabels():
            label.set_x(label.get_position()[0] - 0.01)
        ax.tick_params(axis="y", which="both", length=0)
        ax.tick_params(axis="x", which="both", length=0.1, color="#CED4DE")
        ax.grid(False, axis="x")

    elif chart_type == "bar":
        # --- detect orientation from bar containers ---
        ax.figure.canvas.draw()
        is_horizontal = False
        for container in ax.containers:
            # BarContainer.patches are Rectangles
            widths = [abs(p.get_width()) for p in container.patches]
            heights = [abs(p.get_height()) for p in container.patches]
            if widths and heights:
                # If data runs along X (barh), widths >> heights (band thickness)
                # If data runs along Y (bar), heights >> widths
                if (sum(widths) / len(widths)) > (sum(heights) / len(heights)) * 2.5:
                    is_horizontal = True
                    break

        # --- grid + ticks ---
        ax.grid(False, axis="x")
        ax.grid(False, axis="y")
        ax.tick_params(axis="x", which="both", length=0.1, color="#CED4DE")

        # --- caps + semibold on the categorical axis ---
        if is_horizontal:
            # Y is categorical
            y_ticks = ax.get_yticks()
            y_labels = [t.get_text() for t in ax.get_yticklabels()]
            for lbl in ax.get_yticklabels():
                lbl.set_fontweight("semibold")
                lbl.set_color("#111111")
            if any(y_labels):
                upper = [s.upper() if s else s for s in y_labels]
                try:
                    ax.set_yticks(y_ticks, upper)
                except TypeError:
                    ax.set_yticks(y_ticks)
                    ax.set_yticklabels(upper)

            # zero line should be vertical at x=0
            add_zero_line_v()
        else:
            # X is categorical (standard vertical bars)
            x_ticks = ax.get_xticks()
            x_labels = [t.get_text() for t in ax.get_xticklabels()]
            for lbl in ax.get_xticklabels():
                lbl.set_fontweight("semibold")
                lbl.set_color("#111111")
            if any(x_labels):
                upper = [s.upper() if s else s for s in x_labels]
                try:
                    ax.set_xticks(x_ticks, upper)
                except TypeError:
                    ax.set_xticks(x_ticks)
                    ax.set_xticklabels(upper)

            # zero line should be horizontal at y=0
            add_zero_line_h()

        # --- bar value labels ---
        for container in ax.containers:
            ax.bar_label(
                container,
                fmt="%.0f",
                label_type="edge",
                padding=2,
                fontsize=wb_font_sizes["s"],
                fontweight="semibold",
                color="#111111",
            )



def detect_chart_type(ax):
    lines = ax.get_lines()
    if lines:
        x_data = lines[0].get_xdata()
        if hasattr(x_data, "dtype") and np.issubdtype(x_data.dtype, np.datetime64):
            return "timeseries"
        return "line"

    collections = ax.collections
    if collections:
        return "scatter"

    rects = [patch for patch in ax.patches if isinstance(patch, plt.Rectangle)]
    if rects:
        return "bar"

    return "single_numeric"


def tidy_numeric_ticks(ax, max_ticks=5):
    int_fmt = FuncFormatter(lambda x, pos: f"{int(round(x))}" if x >= 0 else str(x))

    for axis in (ax.xaxis, ax.yaxis):
        locs = axis.get_majorticklocs()
        if len(locs) == 0 or not np.issubdtype(type(locs[0]), np.floating):
            continue

        if np.any(locs > 0):
            axis.set_major_locator(MaxNLocator(nbins=max_ticks, prune=None))
            axis.set_major_formatter(int_fmt)

            for label in axis.get_ticklabels():
                label.set_text(label.get_text())
