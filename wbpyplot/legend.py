from matplotlib.lines import Line2D
from matplotlib.collections import PathCollection


def render_legend_below_plot(fig, handles, labels, spacing, y_position):
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

        custom_handles.append(
            Line2D(
                [],
                [],
                marker="o",
                linestyle="None",
                markersize=7,
                markeredgewidth=0,
                markerfacecolor=color,
            )
        )

    fig.legend(
        custom_handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, y_position + spacing_y),
        bbox_transform=fig.transFigure,
        ncol=min(len(labels), 3),
        frameon=False,
        handletextpad=1.2,
        columnspacing=1.8,
    )


def should_suppress_legend(handles, labels):
    return len(set(labels)) <= 1
