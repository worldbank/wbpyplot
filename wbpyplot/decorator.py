# decorator.py
from functools import wraps
import matplotlib.pyplot as plt
import numpy as np

from .theme import get_dynamic_sizes, wb_rcparams
from .layout import render_title_subtitle_note, compute_total_bottom_margin
from .legend import render_legend_below_plot, should_suppress_legend
from .axis import apply_axis_styling, detect_chart_type, tidy_numeric_ticks
from .number_formatting import format_number
from .colors import (
    resolve_color_cycle_and_label_map,
    apply_color_map_to_axes,
    apply_annotation_text_colors,
    apply_legend_marker_colors,
    apply_cmap_to_mappables,
    build_binned_cmap_and_norm_from_axes,
)


def wb_plot(
    width=1200,
    height=800,
    dpi=120,
    nrows=1,
    ncols=1,
    save_path=None,
    title=None,
    subtitle=None,
    note=None,
    palette=None,
    palette_n=None,
    palette_bins=None,
    palette_bin_mode="linear", 
):
    """
    Create a standardized Matplotlib theme via a decorator for the World Bank with consistent styling,
    titles, legends, and optional export. Handles both discrete and
    continuous color logic.

    The World Bank's data visualization style guide can be accessed [here](https://wbg-vis-design.vercel.app/).

    Parameters
    ----------
    width : int, default=1200
        Width of the figure in pixels.
    height : int, default=800
        Height of the figure in pixels.
    dpi : int, default=120
        Resolution of the figure in dots per inch.
    nrows : int, default=1
        Number of subplot rows.
    ncols : int, default=1
        Number of subplot columns.
    save_path : str or Path, optional
        File path to save the rendered figure. If ``None``, the figure
        is not saved.
    title : str, optional
        Main title displayed at the top of the figure.
    subtitle : str, optional
        Subtitle displayed below the main title.
    note : str, optional
        Footnote or caption displayed at the bottom of the figure.
    palette : str, sequence, or Colormap, optional
        Color palette definition. Supports:
        - Discrete palettes (cycled through categories).
        - Label-mapped palettes (map colors by label).
        - Continuous palettes (generate a Matplotlib Colormap).
    palette_n : int, optional
        Number of colors to sample from the palette.
    palette_bins : int, sequence, or None, default=None
        Binning strategy for continuous palettes:
        - ``None``: no discretization (continuous colormap).
        - int: number of equally spaced bins.
        - sequence: explicit bin edges.
    palette_bin_mode : {"linear", "quantile"}, default="linear"
        Method for discretizing continuous values when ``palette_bins``
        is specified.

    Notes
    -----
    - For discrete (categorical) palettes, the function sets
      ``axes.prop_cycle`` before plotting.
    - For label-mapped palettes, it recolors plot elements and their
      legend entries by label.
    - For continuous palettes, it creates a Colormap and, if bins are
      specified, generates a ``ListedColormap`` and corresponding
      ``BoundaryNorm``. These are applied to compatible artists
      (e.g., ``imshow``, ``pcolormesh``, ``contourf``), and colorbars
      are refreshed automatically.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure object.
    axes : array of matplotlib.axes.Axes
        The subplot axes array.
    """

    def decorator(plot_func):
        @wraps(plot_func)
        def wrapper(*args, **kwargs):
            # Apply global rcparams/theme
            plt.rcParams.update(wb_rcparams)
            font_sizes, spacing = get_dynamic_sizes(width)

            # Figure/axes
            fig, axs = plt.subplots(
                nrows=nrows,
                ncols=ncols,
                figsize=(width / dpi, height / dpi),
                dpi=dpi,
            )
            axs = axs.flatten() if isinstance(axs, (list, np.ndarray)) else [axs]

            # --- Resolve colors (cycle / label_map / text_map / continuous cmap) ---
            cycle, label_map, text_map, cmap = resolve_color_cycle_and_label_map(
                palette=palette,
                n=palette_n,
            )

            # Apply discrete color cycle before plotting
            if cycle is not None:
                for ax in axs:
                    ax.set_prop_cycle(cycle)

            # === User plotting ===
            plot_func(axs, *args, **kwargs)

            # If we have a continuous cmap and binning requested, build binned variants
            binned_cmap, binned_norm = (None, None)
            if cmap is not None and palette_bins is not None:
                binned_cmap, binned_norm = build_binned_cmap_and_norm_from_axes(
                    axs,
                    cmap,
                    bins=palette_bins,
                    mode=str(palette_bin_mode or "linear").lower(),
                )

            # Apply Colormap (and Norm if binned) to mappables; refresh colorbars
            apply_cmap_to_mappables(
                axs,
                binned_cmap if binned_cmap is not None else cmap,
                norm=binned_norm,
            )

            # Label-based recoloring (lines/bars/patches) + legend markers (not text)
            if label_map:
                apply_color_map_to_axes(axs, label_map)
                apply_legend_marker_colors(axs, label_map)

            # Annotation text colors (NOT legend text)
            if text_map:
                apply_annotation_text_colors(axs, text_map)

            # Axes styling / tidy ticks
            for ax in axs:
                chart_type = detect_chart_type(ax)
                apply_axis_styling(ax, font_sizes, spacing, chart_type)
                tidy_numeric_ticks(ax, max_ticks=5)

            # # --- Optional number formatting
            # def try_format(value):
            #     try:
            #         return format_number(value)
            #     except Exception:
            #         return value

            # # Format Y-axis
            # y_labels = ax.get_yticks()
            # ax.set_yticklabels([try_format(y) for y in y_labels])

            # # Format X-axis (only if not timeseries/scatter)
            # if chart_type != 'timeseries' or chart_type != 'scatter':
            #     x_labels = ax.get_xticks()
            #     ax.set_xticklabels([try_format(x) for x in x_labels])

            # --- Titles, subtitles, notes, legend layout ---
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

            # Remove any in-axes legend before rendering the custom one
            if axs[0].get_legend():
                axs[0].get_legend().remove()

            fig.canvas.draw()

            if show_legend:
                legend_y = (
                    total_bottom_margin_frac
                    - note_margin_frac
                    - spacing["xl"] / (fig.get_size_inches()[1] * fig.dpi)
                )
                render_legend_below_plot(fig, handles, labels, spacing, legend_y)

            if save_path:
                fig.savefig(save_path, bbox_inches="tight")
            else:
                plt.show()

        return wrapper

    return decorator
