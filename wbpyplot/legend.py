from matplotlib.lines import Line2D
from matplotlib.collections import PathCollection
import matplotlib.font_manager as font_manager


def render_legend_below_plot(fig, handles, labels, spacing, y_position, x_position=None, legend_title=None, font_sizes=None):
    fig.canvas.draw()
    spacing_y = spacing["xl"] / (fig.get_size_inches()[1] * fig.dpi)
    labels = [label.upper() for label in labels]

    custom_handles = []
    for h, label in zip(handles, labels):
        if isinstance(h, Line2D):
            color = h.get_color()
        elif isinstance(h, PathCollection):
            color = h.get_facecolor()[0] if len(h.get_facecolor()) else "#CED4DE"
        else:
            color = "#CED4DE"

        # Style guide mentions 14px color dot, but this appears to be a visual guideline
        # that doesn't translate directly to Matplotlib's markersize (which is area in points²).
        # Using a reasonable size that looks proportional to the text labels.
        custom_handles.append(
            Line2D(
                [],
                [],
                marker="o",
                linestyle="None",
                markersize=8,  # Reasonable size for legend markers (original was 7)
                markeredgewidth=0,
                markerfacecolor=color,
            )
        )

    # Use provided x_position for left alignment, or default to center
    x_anchor = x_position if x_position is not None else 0.5
    loc = "lower left" if x_position is not None else "lower center"

    # Build keyword arguments for legend
    legend_kwargs = {
        "loc": loc,
        "bbox_to_anchor": (x_anchor, y_position + spacing_y),
        "bbox_transform": fig.transFigure,
        "ncol": min(len(labels), 3),
        "frameon": False,
        "handletextpad": 1.2,
        "columnspacing": 1.8,
    }
    
    # Add legend title with specified styling: size s, weight semibold, line height 120%
    if legend_title:
        legend_kwargs["title"] = legend_title
        title_size = font_sizes["s"] if font_sizes else 12
        legend_kwargs["title_fontproperties"] = font_manager.FontProperties(
            size=title_size,
            weight="semibold",
        )

    # Pass handles and labels as positional arguments (required by Matplotlib)
    leg = fig.legend(custom_handles, labels, **legend_kwargs)
    
    # Left-align legend box so title is to the left and above the first legend item
    if leg is not None:
        leg._legend_box.align = "left"
        # Set legend title line height to 120%
        if legend_title and leg.get_title():
            leg.get_title().set_linespacing(1.2)


def should_suppress_legend(handles, labels):
    return len(set(labels)) <= 1
