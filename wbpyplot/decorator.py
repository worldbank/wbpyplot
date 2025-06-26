import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from functools import wraps

from theme import get_dynamic_sizes, wb_rcparams
from layout import (
    render_title_subtitle_note,
    compute_total_bottom_margin
)
from legend import render_legend_below_plot
from axis import apply_axis_styling, detect_chart_type, should_suppress_legend
from number_formatting import format_number


def wb_plot(
    width=600,
    height=500,
    dpi=100,
    nrows=1,
    ncols=1,
    save_path=None,
    seaborn_style=False,
    title=None,
    subtitle=None,
    note=None
):
    def decorator(plot_func):
        @wraps(plot_func)
        def wrapper(*args, **kwargs):
            if seaborn_style:
                sns.set_theme(style="whitegrid")
            plt.rcParams.update(wb_rcparams)

            font_sizes, spacing = get_dynamic_sizes(width)

            fig, axs = plt.subplots(
                nrows=nrows,
                ncols=ncols,
                figsize=(width / dpi, height / dpi),
                dpi=dpi
            )
            axs = axs.flatten() if isinstance(axs, (list, np.ndarray)) else [axs]

            # Plot first
            plot_func(axs, *args, **kwargs)

            for ax in axs:
                chart_type = detect_chart_type(ax)
                apply_axis_styling(ax, font_sizes, spacing, chart_type)

            def try_format(value):
                try:
                    return format_number(value)
                except Exception:
                    return value
            
            # Format Y-axis
            y_labels = ax.get_yticks()
            ax.set_yticklabels([try_format(y) for y in y_labels])

            # Format X-axis (only if not timeseries/scatter)
            if chart_type != 'timeseries' or chart_type != 'scatter':
                x_labels = ax.get_xticks()
                ax.set_xticklabels([try_format(x) for x in x_labels])

            fig.canvas.draw()
            handles, labels = axs[0].get_legend_handles_labels()

            if should_suppress_legend(handles, labels):
                handles, labels = [], []

            show_legend = bool(handles)

            y_top, note_margin_frac, x_margin_frac = render_title_subtitle_note(
                fig, title, subtitle, note, font_sizes, spacing
            )

            total_bottom_margin_frac = compute_total_bottom_margin(
                fig, axs, handles, note, note_margin_frac, spacing
            )

            fig.subplots_adjust(top=y_top, bottom=total_bottom_margin_frac)

            if axs[0].get_legend():
                axs[0].get_legend().remove()

            fig.canvas.draw()

            if show_legend:
                legend_y = total_bottom_margin_frac - note_margin_frac - spacing["xl"] / (fig.get_size_inches()[1] * fig.dpi)
                render_legend_below_plot(fig, handles, labels, spacing, legend_y)

            if save_path:
                fig.savefig(save_path, bbox_inches='tight')
            else:
                plt.show()

        return wrapper
    return decorator
