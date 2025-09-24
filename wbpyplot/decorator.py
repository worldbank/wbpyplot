from functools import wraps
import matplotlib.pyplot as plt
import numpy as np

from theme import get_dynamic_sizes, wb_rcparams
from layout import render_title_subtitle_note, compute_total_bottom_margin
from legend import render_legend_below_plot, should_suppress_legend
from axis import apply_axis_styling, detect_chart_type, tidy_numeric_ticks
# from .number_formatting import format_number  # optional

from colors import (
    resolve_color_cycle_and_label_map,  # (cycle, label_map, text_map, cmap)
    apply_color_map_to_axes,
    apply_annotation_text_colors,
    apply_legend_marker_colors,
)

# --------------------------------------------------------------------
# Helpers for applying colormaps (continuous or binned)
# --------------------------------------------------------------------
def _apply_cmap_to_mappables(axs, cmap, norm=None):
    """Apply cmap (and optional norm) to imshow/pcolormesh/contourf outputs."""
    if cmap is None and norm is None:
        return
    for ax in axs:
        # Images (imshow)
        for im in getattr(ax, "images", []):
            try:
                if cmap is not None: im.set_cmap(cmap)
                if norm is not None: im.set_norm(norm)
            except Exception:
                pass
        # Collections (pcolormesh, contourf -> QuadMesh, PolyCollection, etc.)
        for coll in ax.collections:
            if hasattr(coll, "set_cmap"):
                try:
                    if cmap is not None: coll.set_cmap(cmap)
                    if norm is not None and hasattr(coll, "set_norm"):
                        coll.set_norm(norm)
                except Exception:
                    pass

def _extract_data_from_mappable(m):
    """Best-effort extract of numeric array from an image/collection for binning."""
    arr = None
    if hasattr(m, "get_array"):
        try:
            arr = m.get_array()
            if arr is not None:
                arr = np.asarray(arr)
        except Exception:
            arr = None
    return arr

def _build_binned_cmap_and_norm_from_axes(axs, cmap, bins, mode):
    """Create a (ListedColormap, BoundaryNorm) from a continuous cmap."""
    import matplotlib.colors as mcolors

    arrays = []
    for ax in axs:
        for im in getattr(ax, "images", []):
            arr = _extract_data_from_mappable(im)
            if arr is not None and arr.size > 0:
                arrays.append(arr)
        for coll in ax.collections:
            arr = _extract_data_from_mappable(coll)
            if arr is not None and arr.size > 0:
                arrays.append(arr)

    if not arrays:
        return None, None

    data = np.concatenate([a.ravel() for a in arrays if np.isfinite(a).any()])
    data = data[np.isfinite(data)]
    if data.size == 0:
        return None, None

    # Compute bin edges
    if hasattr(bins, "__iter__"):
        edges = np.asarray(list(bins), dtype=float)
        if edges.ndim != 1 or edges.size < 2:
            return None, None
        nbins = edges.size - 1
    elif isinstance(bins, int) and bins > 0:
        nbins = bins
        if mode == "quantile":
            qs = np.linspace(0, 1, nbins + 1)
            edges = np.quantile(data, qs)
        else:  # linear
            dmin, dmax = np.nanmin(data), np.nanmax(data)
            if not np.isfinite(dmin) or not np.isfinite(dmax) or dmin == dmax:
                return None, None
            edges = np.linspace(dmin, dmax, nbins + 1)
    else:
        return None, None

    # Colors at bin centers
    centers = 0.5 * (edges[:-1] + edges[1:])
    t = (centers - centers.min()) / (centers.max() - centers.min() + 1e-12)
    sample_colors = cmap(t)

    listed = mcolors.ListedColormap(sample_colors, name=getattr(cmap, "name", "binned"))
    norm = mcolors.BoundaryNorm(edges, ncolors=listed.N, clip=True)
    return listed, norm


def wb_plot(
    width=600,
    height=500,
    dpi=100,
    nrows=1,
    ncols=1,
    save_path=None,
    title=None,
    subtitle=None,
    note=None,
    *,
    palette=None,
    palette_n=None,
    palette_bins=None,           # None | int | sequence of edges
    palette_bin_mode="linear",   # "linear" | "quantile"
):
    """
    Standardizes/stylizes Matplotlib plots (layout, titles, legends, export)
    and applies color logic:

    - Discrete (cycle) palettes: set axes.prop_cycle.
    - Label-map palettes: recolor artists by label (and legend markers).
    - Sequential/diverging palettes: build a Colormap object; if `palette_bins`
      is provided, discretize into bins (linear or quantile).
    """
    def decorator(plot_func):
        @wraps(plot_func)
        def wrapper(*args, **kwargs):
            plt.rcParams.update(wb_rcparams)
            font_sizes, spacing = get_dynamic_sizes(width)

            fig, axs = plt.subplots(
                nrows=nrows,
                ncols=ncols,
                figsize=(width / dpi, height / dpi),
                dpi=dpi,
            )
            axs = axs.flatten() if isinstance(axs, (list, np.ndarray)) else [axs]

            # --- Resolve colors ---
            cycle, label_map, text_map, cmap = resolve_color_cycle_and_label_map(
                palette=palette,
                n=palette_n,
            )

            if cycle is not None:
                for ax in axs:
                    ax.set_prop_cycle(cycle)

            # === User plotting ===
            plot_func(axs, *args, **kwargs)

            # If cmap and binning requested
            binned_cmap, binned_norm = (None, None)
            if cmap is not None and palette_bins is not None:
                binned_cmap, binned_norm = _build_binned_cmap_and_norm_from_axes(
                    axs, cmap, bins=palette_bins, mode=str(palette_bin_mode or "linear").lower()
                )

            _apply_cmap_to_mappables(
                axs,
                binned_cmap if binned_cmap is not None else cmap,
                norm=binned_norm,
            )

            if label_map:
                apply_color_map_to_axes(axs, label_map)
                apply_legend_marker_colors(axs, label_map)

            if text_map:
                apply_annotation_text_colors(axs, text_map)

            for ax in axs:
                chart_type = detect_chart_type(ax)
                apply_axis_styling(ax, font_sizes, spacing, chart_type)
                tidy_numeric_ticks(ax, max_ticks=5)

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
