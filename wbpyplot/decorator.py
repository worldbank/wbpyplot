# decorator.py
from functools import wraps
import inspect
import matplotlib.pyplot as plt
import numpy as np

from .theme import get_dynamic_sizes, wb_rcparams
from .layout import render_title_subtitle_note, compute_total_bottom_margin, px_to_fig_frac
from .legend import render_legend_below_plot, should_suppress_legend
from .axis import apply_axis_styling, detect_chart_type, tidy_numeric_ticks
from matplotlib.collections import PathCollection
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
    legend_title=None,
    palette=None,
    palette_n=None,
    palette_bins=None,
    palette_bin_mode="linear",
    include_insets=False,
    backend="mpl",
    show=True,
):
    """
    Create a standardized plotting theme via a decorator for the World Bank with consistent styling,
    titles, legends, and optional export. Handles both discrete and
    continuous color logic. Supports both Matplotlib and Plotly backends.

    The World Bank's data visualization style guide can be accessed [here](https://wbg-vis-design.vercel.app/).

    Parameters
    ----------
    width : int, default=1200
        Width of the figure in pixels.
    height : int, default=800
        Height of the figure in pixels.
    dpi : int, default=120
        Resolution of the figure in dots per inch (Matplotlib only).
    nrows : int, default=1
        Number of subplot rows (Matplotlib only).
    ncols : int, default=1
        Number of subplot columns (Matplotlib only).
    save_path : str or Path, optional
        File path to save the rendered figure. If ``None``, the figure
        is not saved. For Plotly backend, saves as HTML.
    title : str, optional
        Main title displayed at the top of the figure.
    subtitle : str, optional
        Subtitle displayed below the main title.
    note : str, optional
        Footnote or caption displayed at the bottom of the figure.
    legend_title : str, optional
        Title displayed above the legend entries in bold font. If provided,
        appears above the legend keys/icons.
    palette : str, sequence, or Colormap, optional
        Color palette definition. Supports:
        - Discrete palettes (cycled through categories).
        - Label-mapped palettes (map colors by label).
        - Continuous palettes (generate a Matplotlib Colormap or Plotly colorscale).
    palette_n : int, optional
        Number of colors to sample from the palette.
    palette_bins : int, sequence, or None, default=None
        Binning strategy for continuous palettes (Matplotlib only):
        - ``None``: no discretization (continuous colormap).
        - int: number of equally spaced bins.
        - sequence: explicit bin edges.
    palette_bin_mode : {"linear", "quantile"}, default="linear"
        Method for discretizing continuous values when ``palette_bins``
        is specified (Matplotlib only).
    include_insets : bool, default=False
        Whether to include inset axes in styling (Matplotlib only).
    backend : {"mpl", "plotly"}, default="mpl"
        Backend to use for rendering:
        - ``"mpl"``: Matplotlib backend (default).
        - ``"plotly"``: Plotly backend for interactive plots.
    show : bool, default=True
        Whether to automatically display the figure. If ``False``, the figure
        is created but not shown (useful for programmatic use).

    Notes
    -----
    **Matplotlib Backend:**
    - For discrete (categorical) palettes, the function sets
      ``axes.prop_cycle`` before plotting.
    - For label-mapped palettes, it recolors plot elements and their
      legend entries by label.
    - For continuous palettes, it creates a Colormap and, if bins are
      specified, generates a ``ListedColormap`` and corresponding
      ``BoundaryNorm``. These are applied to compatible artists
      (e.g., ``imshow``, ``pcolormesh``, ``contourf``), and colorbars
      are refreshed automatically.

    **Plotly Backend:**
    - The decorated function should accept ``fig`` as the first parameter
      (similar to Matplotlib's ``fig, axs`` signature).
    - Palettes are applied via Plotly's ``colorway`` (discrete) or
      ``colorscale`` (continuous) mechanisms.
    - Title, subtitle, and note are rendered via Plotly's layout system.
    - Legends are positioned below the plot automatically.

    Examples
    --------
    **Matplotlib backend (default):**

    .. code-block:: python

        import pandas as pd
        import numpy as np

        @wb_plot(title="GDP Over Time", subtitle="2010-2020")
        def plot_gdp(fig, axs, df):
            ax = axs[0]
            ax.plot(df["year"], df["gdp"], label="GDP")
            ax.set_ylabel("GDP (billions USD)")

        # Create and call with dataframe
        df = pd.DataFrame({"year": range(2010, 2021), "gdp": np.random.randn(11) * 100 + 500})
        plot_gdp(df)  # Pass dataframe as argument

    **Plotly backend:**

    .. code-block:: python

        import pandas as pd
        import plotly.graph_objects as go

        @wb_plot(title="GDP Over Time", subtitle="2010-2020", backend="plotly")
        def plot_gdp_plotly(fig, df):
            fig.add_scatter(x=df["year"], y=df["gdp"], name="GDP", mode="lines")
            fig.update_yaxes(title_text="GDP (billions USD)")

        # Create and call with dataframe
        df = pd.DataFrame({"year": range(2010, 2021), "gdp": np.random.randn(11) * 100 + 500})
        plot_gdp_plotly(df)  # Pass dataframe as argument

    Returns
    -------
    fig : matplotlib.figure.Figure or plotly.graph_objects.Figure
        The created figure object. Type depends on ``backend``.
    axes : array of matplotlib.axes.Axes, optional
        The subplot axes array (Matplotlib backend only).
    """

    def decorator(plot_func):
        @wraps(plot_func)
        def wrapper(*args, **kwargs):
            if backend == "mpl":
                return _render_mpl(
                    plot_func,
                    args,
                    kwargs,
                    width=width,
                    height=height,
                    dpi=dpi,
                    nrows=nrows,
                    ncols=ncols,
                    save_path=save_path,
                    title=title,
                    subtitle=subtitle,
                    note=note,
                    legend_title=legend_title,
                    palette=palette,
                    palette_n=palette_n,
                    palette_bins=palette_bins,
                    palette_bin_mode=palette_bin_mode,
                    include_insets=include_insets,
                    show=show,
                )
            elif backend == "plotly":
                return _render_plotly(
                    plot_func,
                    args,
                    kwargs,
                    width=width,
                    height=height,
                    save_path=save_path,
                    title=title,
                    subtitle=subtitle,
                    note=note,
                    legend_title=legend_title,
                    palette=palette,
                    palette_n=palette_n,
                    show=show,
                )
            else:
                raise ValueError(
                    f"Unknown backend {backend!r}. Must be 'mpl' or 'plotly'."
                )

        return wrapper

    return decorator


def _render_mpl(
    plot_func,
    args,
    kwargs,
    *,
    width,
    height,
    dpi,
    nrows,
    ncols,
    save_path,
    title,
    subtitle,
    note,
    legend_title,
    palette,
    palette_n,
    palette_bins,
    palette_bin_mode,
    include_insets,
    show,
):
    """Render using Matplotlib backend."""
    # Apply global rcparams/theme
    plt.rcParams.update(wb_rcparams)
    
    # Calculate figure size in inches
    figsize_inches = (width / dpi, height / dpi)
    
    # Get base font sizes and spacing (tuned for embedded output e.g. Quarto)
    font_sizes, spacing = get_dynamic_sizes(width)
    # Slight scale for resizing; if portrait, scale down so plot area isn't squished
    scale_factor = 0.95
    if height > width:
        scale_factor *= width / height
    font_sizes = {k: max(8, int(v * scale_factor)) for k, v in font_sizes.items()}

    # Figure/axes
    fig, axs = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=figsize_inches,
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
    # Support both legacy signatures (axs, *args, **kwargs)
    # and new signatures (fig, axs, *args, **kwargs).
    sig = inspect.signature(plot_func)
    params = list(sig.parameters.values())
    
    # Check if function expects 'fig' as first parameter
    # This indicates the new signature style: def func(fig, axs, ...)
    has_fig_param = len(params) >= 1 and params[0].name == "fig"
    
    if has_fig_param and len(params) >= 2:
        # New signature: def func(fig, axs, *args, **kwargs)
        # Pass fig and axs, then all user-provided args
        plot_func(fig, axs, *args, **kwargs)
    else:
        # Legacy signature: def func(axs, *args, **kwargs)
        # Pass axs, then all user-provided args
        plot_func(axs, *args, **kwargs)

    # Determine which axes to include in styling / color handling.
    if include_insets:
        axes_for_styling = fig.get_axes()
    else:
        axes_for_styling = axs

    # If we have a continuous cmap and binning requested, build binned variants
    binned_cmap, binned_norm = (None, None)
    if cmap is not None and palette_bins is not None:
        binned_cmap, binned_norm = build_binned_cmap_and_norm_from_axes(
            axes_for_styling,
            cmap,
            bins=palette_bins,
            mode=str(palette_bin_mode or "linear").lower(),
        )

    # Apply Colormap (and Norm if binned) to mappables; refresh colorbars
    apply_cmap_to_mappables(
        axes_for_styling,
        binned_cmap if binned_cmap is not None else cmap,
        norm=binned_norm,
    )

    # Label-based recoloring (lines/bars/patches) + legend markers (not text)
    if label_map:
        apply_color_map_to_axes(axes_for_styling, label_map)
        apply_legend_marker_colors(axes_for_styling, label_map)

    # Annotation text colors (NOT legend text)
    if text_map:
        apply_annotation_text_colors(axes_for_styling, text_map)

    # Axes styling / tidy ticks
    for ax in axes_for_styling:
        chart_type = detect_chart_type(ax)
        apply_axis_styling(ax, font_sizes, spacing, chart_type)
        tidy_numeric_ticks(ax, max_ticks=5, chart_type=chart_type)

    # Scatter markers: larger size with white outline
    _SCATTER_MARKER_AREA = 42  # ~6.5pt radius
    for ax in axes_for_styling:
        for col in ax.collections:
            if isinstance(col, PathCollection):
                sizes = col.get_sizes()
                n = sizes.size if sizes is not None and sizes.size else 0
                if n == 0:
                    fc = col.get_facecolors()
                    n = fc.shape[0] if fc.size else 0
                if n:
                    col.set_sizes(np.full(n, _SCATTER_MARKER_AREA))
                col.set_edgecolors("white")
                col.set_linewidths(0.8)

    # --- Titles, subtitles, notes, legend layout ---
    fig.canvas.draw()
    handles, labels = axs[0].get_legend_handles_labels()
    existing_ax_legend = axs[0].get_legend()
    # GeoPandas categorical maps can build an in-axes Legend artist while
    # get_legend_handles_labels() still returns empty; preserve that legend.
    has_in_axes_only_legend = existing_ax_legend is not None and len(handles) == 0 and len(labels) == 0

    if should_suppress_legend(handles, labels):
        handles, labels = [], []
    show_legend = bool(handles)

    y_top, note_margin_frac, x_margin_frac = render_title_subtitle_note(
        fig, title, subtitle, note, font_sizes, spacing
    )
    
    # For line/timeseries charts: move Y-axis title to top (underneath subtitle, horizontal)
    for ax in axes_for_styling:
        chart_type = detect_chart_type(ax)
        if chart_type in ("line", "timeseries"):
            ylabel_text = ax.get_ylabel()
            if ylabel_text:
                # Remove Y-axis label from left side
                ax.set_ylabel("")
                # Add Y-axis label as text annotation at top (underneath subtitle)
                fig.canvas.draw()
                renderer = fig.canvas.get_renderer()
                ylabel_artist = fig.text(
                    x_margin_frac,
                    y_top,
                    ylabel_text,
                    fontsize=font_sizes["s"],
                    fontweight="semibold",
                    color="#111111",
                    ha="left",
                    va="top",
                    linespacing=1.2,
                )
                fig.canvas.draw()
                bbox = ylabel_artist.get_window_extent(renderer=renderer)
                ylabel_height_frac = bbox.height / (fig.get_size_inches()[1] * fig.dpi)
                # Adjust y_top to account for Y-axis label
                y_top -= ylabel_height_frac + px_to_fig_frac(spacing["s"], fig, "y")
                break  # Only do this for the first axis
    
    total_bottom_margin_frac = compute_total_bottom_margin(
        fig, axs, handles, note, note_margin_frac, spacing
    )
    
    # Left/right margins: keep compact so plot area gets more width
    left_margin_frac = px_to_fig_frac(spacing["s"], fig, "x")
    right_margin_frac = px_to_fig_frac(spacing["s"], fig, "x")
    has_ylabel = any(ax.get_ylabel() for ax in axs)
    if has_ylabel:
        left_margin_frac += px_to_fig_frac(spacing["l"], fig, "x")
    
    # Apply margins with padding to prevent overlap
    # Use subplots_adjust with all margins set
    fig.subplots_adjust(
        top=y_top,
        bottom=total_bottom_margin_frac,
        left=left_margin_frac,
        right=1.0 - right_margin_frac,
        hspace=0.2 if nrows > 1 else None,  # Add spacing between subplots if multiple rows
        wspace=0.2 if ncols > 1 else None,  # Add spacing between subplots if multiple columns
    )
    
    # Apply tight_layout AFTER subplots_adjust to ensure no overlap.
    # Use moderate padding so that spacing feels tight but safe in
    # interactive environments (including window resizes).
    try:
        fig.tight_layout(
            rect=[None, total_bottom_margin_frac, None, y_top],
            pad=1.5,
            h_pad=1.2 if nrows > 1 else 0.8,
            w_pad=1.2 if ncols > 1 else 0.8,
        )
    except Exception:
        # If tight_layout fails (e.g., incompatible backend), 
        # subplots_adjust should still provide reasonable spacing
        pass

    # Remove in-axes legend only when replacing with the WB custom legend.
    # Keep map legends that exist as in-axes Legend artists only.
    if show_legend and existing_ax_legend and not has_in_axes_only_legend:
        existing_ax_legend.remove()

    fig.canvas.draw()

    if show_legend:
        # Place legend strictly within the reserved bottom margin, between
        # the note block (if any) and the bottom edge of the axes. The axes
        # plot area should remain completely free of legend boxes.
        # We anchor the legend just above the notes with a small vertical
        # padding so its top cannot cross into the axes region.
        usable_margin = max(total_bottom_margin_frac - note_margin_frac, 0.0)
        # Small padding above the notes, in figure fraction:
        legend_padding = min(
            px_to_fig_frac(spacing["m"], fig, "y"),
            usable_margin * 0.4,  # don't eat too much of the band
        )
        legend_y = note_margin_frac + legend_padding
        render_legend_below_plot(fig, handles, labels, spacing, legend_y, x_margin_frac, legend_title, font_sizes)
    
    # Final tight_layout call after all elements (including legend) are rendered
    # This ensures proper spacing even when the window is resized
    fig.canvas.draw()
    try:
        fig.tight_layout(
            rect=[None, total_bottom_margin_frac, None, y_top],
            pad=1.5,
            h_pad=1.2 if nrows > 1 else 0.8,
            w_pad=1.2 if ncols > 1 else 0.8,
        )
    except Exception:
        pass
    
    # Add resize callback to handle window resizing in interactive environments.
    # This recalculates spacing when the window is resized by re-applying
    # tight_layout with the same moderate padding.
    def on_resize(event):
        """Handle figure resize events by recalculating layout."""
        if event.canvas != fig.canvas:
            return
        try:
            # Reapply tight_layout with the same padding used above.
            fig.tight_layout(
                rect=[None, total_bottom_margin_frac, None, y_top],
                pad=1.5,
                h_pad=1.2 if nrows > 1 else 0.8,
                w_pad=1.2 if ncols > 1 else 0.8,
            )
            fig.canvas.draw_idle()  # Redraw without blocking
        except Exception:
            # If resize handling fails, try basic tight_layout
            try:
                fig.tight_layout(pad=1.5)
                fig.canvas.draw_idle()
            except Exception:
                pass
    
    # Connect resize event handler
    try:
        fig.canvas.mpl_connect('resize_event', on_resize)
    except Exception:
        # If event connection fails, continue without resize handling
        pass

    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
    elif show:
        plt.show()

    # Return None when showing so Quarto/Jupyter don't print (fig, axs)
    return None if show else (fig, axs)


def _render_plotly(
    plot_func,
    args,
    kwargs,
    *,
    width,
    height,
    save_path,
    title,
    subtitle,
    note,
    legend_title,
    palette,
    palette_n,
    show,
):
    """Render using Plotly backend."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        raise ImportError(
            "Plotly backend requires plotly package. Install with: pip install plotly"
        )

    # Get dynamic font sizes and spacing (matching Matplotlib)
    font_sizes, spacing = get_dynamic_sizes(width)
    
    # Get the actual font name that Matplotlib uses (from OpenSans.ttf)
    # This ensures consistency between Matplotlib and Plotly backends
    try:
        font_family_name = wb_rcparams.get("font.family", "Open Sans")
        # If it's a list (Matplotlib can return lists), take the first one
        if isinstance(font_family_name, list):
            font_family_name = font_family_name[0]
    except Exception:
        font_family_name = "Open Sans"  # Fallback

    # Create figure
    fig = go.Figure()

    # Resolve colors for Plotly
    cycle, label_map, text_map, cmap = resolve_color_cycle_and_label_map(
        palette=palette,
        n=palette_n,
    )

    # Store colorscale for later application to traces
    colorscale = None
    if cmap is not None:
        # Convert Matplotlib colormap to Plotly colorscale
        colorscale = []
        for i in range(256):
            rgba = cmap(i / 255.0)
            rgb = f"rgb({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)})"
            colorscale.append([i / 255.0, rgb])

    # Apply colorway for discrete palettes
    if cycle is not None:
        colors = cycle.by_key().get("color", [])
        if colors:
            fig.update_layout(colorway=colors)
    else:
        # Use default Matplotlib color cycle when no palette is specified
        # This ensures Plotly uses the same default colors as Matplotlib
        default_cycle = wb_rcparams.get("axes.prop_cycle")
        if default_cycle is not None:
            default_colors = default_cycle.by_key().get("color", [])
            if default_colors:
                fig.update_layout(colorway=default_colors)

    # Call user plotting function
    # For Plotly, we pass fig as the first argument (similar to Matplotlib's fig, axs)
    sig = inspect.signature(plot_func)
    n_params = len(
        [
            p
            for p in sig.parameters.values()
            if p.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ]
    )

    if n_params <= 1:
        # Legacy: def func(fig, *args, **kwargs) - but for Plotly we always pass fig
        plot_func(fig, *args, **kwargs)
    else:
        # New: def func(fig, *args, **kwargs)
        plot_func(fig, *args, **kwargs)

    # Capture Y-axis title immediately after user function (before we modify layout)
    # This is needed for line charts with temporal X-axis where we move Y-axis title to top
    yaxis_title_text_early = None
    try:
        if hasattr(fig.layout, "yaxis") and hasattr(fig.layout.yaxis, "title"):
            title_obj = fig.layout.yaxis.title
            if hasattr(title_obj, "text"):
                yaxis_title_text_early = title_obj.text
                if yaxis_title_text_early == "":
                    yaxis_title_text_early = None
    except (AttributeError, TypeError):
        pass

    # Apply colorscale to traces that support it (if continuous palette)
    if colorscale:
        for trace in fig.data:
            # Apply colorscale to traces that have z values (choropleth, heatmaps, etc.)
            if hasattr(trace, "z") and trace.z is not None:
                trace.colorscale = colorscale
                # Choropleth from px.choropleth often uses layout.coloraxis; clear it so
                # this trace uses its own colorscale (WB palette).
                if hasattr(trace, "coloraxis") and getattr(trace, "coloraxis", None):
                    trace.coloraxis = None
            # For scatter plots with color values
            elif hasattr(trace, "marker") and hasattr(trace.marker, "color"):
                if isinstance(trace.marker.color, (list, np.ndarray)):
                    trace.marker.colorscale = colorscale

    # Apply label-based color mapping if needed
    if label_map:
        # Update trace colors based on legend labels
        for trace in fig.data:
            if hasattr(trace, "name") and trace.name in label_map:
                color = label_map[trace.name]
                if hasattr(trace, "marker"):
                    trace.marker.color = color
                if hasattr(trace, "line"):
                    trace.line.color = color
                if hasattr(trace, "fillcolor"):
                    trace.fillcolor = color
    
    # Apply default line width and marker size to traces
    # Plotly marker size 6 (keep previous size); white outline on scatter markers
    for trace in fig.data:
        if hasattr(trace, "line") and trace.line is not None:
            if not hasattr(trace.line, "width") or trace.line.width is None:
                trace.line.width = 2.0
        # Scatter traces only: marker size and white outline (Bar traces have no marker.size)
        if (
            getattr(trace, "type", None) == "scatter"
            and hasattr(trace, "marker")
            and trace.marker is not None
        ):
            if not hasattr(trace.marker, "size") or trace.marker.size is None:
                trace.marker.size = 8
            trace.marker.line = dict(color="white", width=1)

    # Choropleth/map: detect so we can set geo.domain and apply WB layout
    has_choropleth = any(getattr(t, "type", None) == "choropleth" for t in fig.data)

    # Bar charts: value labels beside bars (like matplotlib bar_label), no grid in bar direction
    has_bar = any(getattr(t, "type", None) == "bar" for t in fig.data)
    is_bar_chart_horizontal = any(
        getattr(t, "orientation", None) == "h" for t in fig.data if getattr(t, "type", None) == "bar"
    ) if has_bar else False
    if has_bar:
        def _bar_fmt(v):
            if isinstance(v, (int, float)):
                return str(int(v)) if v == int(v) else str(round(v, 2))
            return str(v)
        for trace in fig.data:
            if getattr(trace, "type", None) != "bar":
                continue
            # Value labels beside bars (values are in y for vertical, x for horizontal)
            vals = trace.y if getattr(trace, "orientation", None) != "h" else trace.x
            if vals is not None:
                vlist = list(vals) if hasattr(vals, "__iter__") and not isinstance(vals, str) else [vals]
                trace.text = [_bar_fmt(v) for v in vlist]
                trace.textposition = "outside"

    # Detect if this is a line chart with temporal X-axis (matching Matplotlib behavior)
    # For line charts with temporal X-axis only: remove X-axis label and tick marks.
    # Do NOT apply to scatter plots or other chart types (they keep X-axis title).
    # A line chart is temporal if: 1) trace mode includes "lines" (not just "markers"),
    # 2) X-axis is datetime-like OR numeric.
    is_line_chart_with_temporal_x = False
    if fig.data:
        # Only treat as line chart when traces actually draw lines (mode contains "lines")
        has_lines = any(
            hasattr(trace, "mode") and trace.mode and "lines" in str(trace.mode)
            for trace in fig.data
        )

        if has_lines:
            # Check if Plotly has detected it as a date axis (user may have set this)
            if hasattr(fig.layout, "xaxis") and hasattr(fig.layout.xaxis, "type"):
                if fig.layout.xaxis.type in ("date", "date-time"):
                    is_line_chart_with_temporal_x = True
            
            # Also check X-axis data for datetime-like values
            if not is_line_chart_with_temporal_x:
                for trace in fig.data:
                    if hasattr(trace, "x") and trace.x is not None:
                        x_data = trace.x
                        # Check if it's datetime-like (pandas datetime, numpy datetime64)
                        if hasattr(x_data, "dtype"):
                            if np.issubdtype(x_data.dtype, np.datetime64):
                                is_line_chart_with_temporal_x = True
                                break
                        elif isinstance(x_data, (list, tuple)) and len(x_data) > 0:
                            # Check first element - could be pandas Timestamp, datetime, or date string
                            first_val = x_data[0]
                            if hasattr(first_val, "__class__"):
                                class_name = first_val.__class__.__name__
                                if any(dt_type in class_name for dt_type in ["Timestamp", "datetime", "date", "Date"]):
                                    is_line_chart_with_temporal_x = True
                                    break
            
            # If still not detected, check if X-axis is numeric (line charts with numeric X are typically temporal)
            # This handles cases like years (2010, 2011, etc.) that aren't datetime objects
            if not is_line_chart_with_temporal_x:
                for trace in fig.data:
                    if hasattr(trace, "x") and trace.x is not None:
                        x_data = trace.x
                        # Check if it's numeric (int or float)
                        if hasattr(x_data, "dtype"):
                            if np.issubdtype(x_data.dtype, np.number):
                                is_line_chart_with_temporal_x = True
                                break
                        elif isinstance(x_data, (list, tuple)) and len(x_data) > 0:
                            # Check if first element is numeric
                            first_val = x_data[0]
                            if isinstance(first_val, (int, float, np.integer, np.floating)):
                                is_line_chart_with_temporal_x = True
                                break

    # Preserve user-set axis titles (e.g. scatter: xaxis_title="GDP per capita")
    # Only clear titles for temporal line charts; otherwise keep what the user set
    def _get_axis_title(fig, axis_name):
        try:
            axis = getattr(fig.layout, axis_name, None)
            if axis is None:
                return None
            title = getattr(axis, "title", None)
            if title is None:
                return None
            text = getattr(title, "text", None)
            return str(text).strip() or None
        except (AttributeError, TypeError):
            return None

    existing_xaxis_title = _get_axis_title(fig, "xaxis")
    existing_yaxis_title = _get_axis_title(fig, "yaxis")

    def _build_axis_title_dict(is_temporal, existing_title, font_size, font_family, standoff=None):
        """Build x/y axis title dict. Only set 'text' when we have a value so merge preserves user title."""
        d = {
            "font": {
                "size": font_size,
                "color": "#111111",
                "family": f"{font_family}, sans-serif",
                "weight": "bold",
            },
        }
        if is_temporal:
            d["text"] = ""
        elif existing_title:
            d["text"] = existing_title
        if standoff is not None:
            d["standoff"] = standoff
        return d

    # Helper function to estimate text height in figure fraction
    # Approximates Matplotlib's bbox.height calculation
    def estimate_text_height_frac(text, font_size, fig_height, line_height=1.2):
        """Estimate text height as fraction of figure height."""
        # Approximate: font_size * line_height_factor / fig_height
        # Default 1.2 (120%) for title/subtitle, 1.5 (150%) for notes per style guide
        # and accounting for font metrics
        lines = len(text.split('\n')) if text else 1
        estimated_px = font_size * line_height * lines * 1.2  # Extra factor for font metrics
        return estimated_px / fig_height
    
    # Helper function to convert pixels to figure fraction
    def px_to_fig_frac(px, axis="y"):
        """Convert pixels to figure fraction (matching Matplotlib's px_to_fig_frac)."""
        if axis == "y":
            return px / height
        else:
            return px / width
    
    # Calculate spacing fractions (matching Matplotlib approach)
    spacing_frac = {k: px_to_fig_frac(v, "y") for k, v in spacing.items()}
    # Align title, subtitle, and notes with the left edge of the image
    # Use minimal padding (xxs) so text starts at the figure edge
    margin_x_frac = px_to_fig_frac(spacing["xxs"], "x")
    
    # Calculate title/subtitle positions dynamically (matching Matplotlib)
    annotations = []
    y_top = 1.0 - spacing_frac["xl"]  # Start from top with xl spacing
    
    if title:
        # Estimate title height
        title_height_frac = estimate_text_height_frac(title, font_sizes["l"], height)
        # Title as separate annotation (better control than layout.title)
        annotations.append({
            "text": f"<b>{title}</b>",  # Bold title
            "showarrow": False,
            "xref": "paper",
            "yref": "paper",
            "x": margin_x_frac,
            "y": y_top,
            "xanchor": "left",
            "yanchor": "top",
            "font": {
                "size": font_sizes["l"],
                "color": "#111111",
                "family": f"{font_family_name}, sans-serif",
            },
        })
        # Spacing between title and subtitle
        y_top -= title_height_frac + spacing_frac["s"]  # Reduced spacing
    
    if subtitle:
        # Estimate subtitle height
        subtitle_height_frac = estimate_text_height_frac(subtitle, font_sizes["m"], height)
        # Subtitle as separate annotation (matching Matplotlib's separate text element)
        annotations.append({
            "text": subtitle,
            "showarrow": False,
            "xref": "paper",
            "yref": "paper",
            "x": margin_x_frac,
            "y": y_top,
            "xanchor": "left",
            "yanchor": "top",
            "font": {
                "size": font_sizes["m"],
                "color": "#666666",
                "family": f"{font_family_name}, sans-serif",
            },
        })
        y_top -= subtitle_height_frac + spacing_frac["m"]  # Changed from "xl" to "m" for tighter spacing
    
    # Apply WB styling via layout (matching Matplotlib styling)
    layout_updates = {
        "width": width,
        "height": height,
        "font": {
            "family": f"{font_family_name}, sans-serif",  # Use same font as Matplotlib
            "size": font_sizes["s"],  # Use dynamic font size
            "color": "#111111",
        },
        "plot_bgcolor": "white",
        "paper_bgcolor": "white",
        "xaxis": {
            "gridcolor": "#CED4DE",  # grey200 per style guide
            "gridwidth": 1,  # 1px per style guide
            "griddash": "4,2",  # dash 4 2 per style guide
            "showgrid": not is_line_chart_with_temporal_x,  # Remove grid for temporal line charts
            "zeroline": False,
            "tickfont": {"size": font_sizes["s"], "color": "#666666"},
            "title": _build_axis_title_dict(
                is_line_chart_with_temporal_x, existing_xaxis_title, font_sizes["s"], font_family_name, standoff=None
            ),
            "showticklabels": True,  # Keep tick labels visible (year values)
            "ticklen": 0,  # No tick marks (remove visual marks but keep labels)
        },
        "yaxis": {
            "gridcolor": "#CED4DE",  # grey200 per style guide
            "gridwidth": 1,  # 1px per style guide
            "griddash": "4,2",  # dash 4 2 per style guide
            "showgrid": not is_bar_chart_horizontal,  # No grid in bar direction (horizontal bars extend along x)
            "zeroline": False,
            "tickfont": {"size": font_sizes["s"], "color": "#666666"},
            "title": _build_axis_title_dict(
                is_line_chart_with_temporal_x, existing_yaxis_title, font_sizes["s"], font_family_name, standoff=0
            ),
            "showticklabels": True,
            "ticklen": 0,  # No tick marks on Y axis (matches Matplotlib)
        },
        "margin": {
            "l": spacing["m"] * 2,
            "r": spacing["m"],
            "t": spacing["m"],  # Minimal top margin - annotations handle positioning
            "b": spacing["xl"] * 2,
        },
        # Tooltip (hover label) styling per World Bank style guide
        # https://wbg-vis-design.vercel.app/chartelements#tooltips
        # Card: white bg, border grey200; header: size s, semibold; label: size s, regular; number: size m, bold
        "hoverlabel": {
            "bgcolor": "white",
            "bordercolor": "#CED4DE",  # grey200
            "font": {
                "size": font_sizes["s"],
                "color": "#111111",
                "family": f"{font_family_name}, sans-serif",
            },
            "grouptitlefont": {
                "size": font_sizes["s"],
                "color": "#111111",
                "family": f"{font_family_name}, sans-serif",
                "weight": 600,  # semibold per style guide header
            },
            "align": "left",
        },
    }
    
    # Set top margin based on title/subtitle height (dynamic calculation)
    # Since annotations are positioned from y_top=1.0, we only need minimal padding
    if title or subtitle:
        # Calculate top margin: just enough to prevent clipping
        top_margin_px = spacing["m"]  # Minimal initial spacing
        if title:
            top_margin_px += font_sizes["l"] * 1.2 * 1.2 + spacing["xxs"]
        if subtitle:
            top_margin_px += font_sizes["m"] * 1.2 * 1.2 + spacing["m"]
        layout_updates["margin"]["t"] = int(top_margin_px)

    # Handle note as annotation (matching Matplotlib's dynamic positioning)
    notes_to_render = []
    if note:
        if isinstance(note, str):
            notes_to_render = [("", note)]
        elif isinstance(note, tuple):
            notes_to_render = [note]
        elif isinstance(note, list):
            notes_to_render = note
    
    # Calculate note positions dynamically
    # Start notes from bottom (no initial m spacing) - xl spacing will be added from note bottom edge
    y_note = 0.0  # Start from bottom (no initial spacing)
    last_note_bottom_edge = None  # Track bottom edge of last note for spacing calculation
    
    for label, text in notes_to_render:
        # Combine label and text (label in bold, matching Matplotlib)
        if label:
            note_text = f"<b>{label}</b> {text}"
        else:
            note_text = text
        
        # Estimate note height (notes use 150% line height per style guide)
        note_height_frac = estimate_text_height_frac(note_text, font_sizes["s"], height, line_height=1.5)
        
        # Track bottom edge of this note (before moving y_note up)
        last_note_bottom_edge = y_note
        
        # Render note as annotation
        # Note: Plotly doesn't support line-height in annotations, but we use 150% in estimate_text_height_frac
        annotations.append({
            "text": note_text,
            "showarrow": False,
            "xref": "paper",
            "yref": "paper",
            "x": margin_x_frac,
            "y": y_note,
            "xanchor": "left",
            "yanchor": "bottom",
            "font": {
                "size": font_sizes["s"],
                "color": "#666666",  # textSubtle color per style guide
                "family": f"{font_family_name}, sans-serif",
            },
        })
        
        y_note += note_height_frac + spacing_frac["m"]  # Add spacing between notes (m spacing between multiple notes)
    
    # note_margin_frac: position after last note (for compatibility with other calculations)
    note_margin_frac = y_note if notes_to_render else 0
    
    # Check if there are legend items and uppercase labels to match Matplotlib
    has_legend = len(fig.data) > 0 and any(
        hasattr(trace, "name") and trace.name and trace.name != ""
        for trace in fig.data
    )
    
    # Uppercase legend labels to match Matplotlib behavior
    if has_legend:
        for trace in fig.data:
            if hasattr(trace, "name") and trace.name:
                trace.name = trace.name.upper()
    
    # Calculate bottom margin dynamically (matching Matplotlib's compute_total_bottom_margin)
    # X-axis label: user-set title (existing_xaxis_title) or we set it in layout
    has_xlabel = bool(existing_xaxis_title) or (
        layout_updates["xaxis"].get("title", {}).get("text") is not None
    )
    
    xlabel_spacing_frac = (
        spacing_frac["xl"] * 2 if has_xlabel
        else spacing_frac["xl"] * 1
    )
    
    legend_spacing_frac = spacing_frac["xl"]
    
    if has_legend and not notes_to_render:
        # Order: plot -> X-axis title -> legend -> bottom
        # Ensure xl spacing from legend to bottom edge
        bottom_margin_frac = (
            xlabel_spacing_frac  # X-axis title space (closest to plot)
            + legend_spacing_frac
            + spacing_frac["xl"] * 2  # Space for legend
            + spacing_frac["xl"]  # xl spacing from legend to bottom
        )
    elif has_legend and notes_to_render:
        # Order: plot -> X-axis title -> legend -> notes -> bottom
        # Ensure xl spacing from notes to bottom edge
        bottom_margin_frac = (
            xlabel_spacing_frac  # X-axis title space (closest to plot)
            + legend_spacing_frac
            + spacing_frac["xl"] * 2  # Space for legend
            + note_margin_frac  # Notes below legend
            + spacing_frac["xl"]  # xl spacing from notes to bottom
        )
    elif notes_to_render:
        # Order: plot -> X-axis title -> notes -> bottom
        # Ensure L spacing from bottom edge of last note to figure bottom
        # last_note_bottom_edge is the y-position of the last note's bottom edge (as fraction)
        # The note's bottom edge is at: last_note_bottom_edge * height pixels from bottom
        # We want L spacing from there, so margin = last_note_bottom_edge * height + spacing["l"]
        last_note_bottom_px = last_note_bottom_edge * height
        bottom_margin_px = last_note_bottom_px + spacing["l"]  # L spacing from note bottom edge
        bottom_margin_frac = bottom_margin_px / height
    else:
        # Order: plot -> X-axis title -> bottom
        # Ensure L spacing from X-axis title to bottom edge
        # Convert xlabel_spacing_frac to pixels, add L spacing in pixels
        xlabel_spacing_px = xlabel_spacing_frac * height
        bottom_margin_px = xlabel_spacing_px + spacing["l"]  # Use absolute pixels for L spacing
        bottom_margin_frac = bottom_margin_px / height
    
    # Convert fraction to pixels for margin
    layout_updates["margin"]["b"] = int(bottom_margin_frac * height)
    
    # Calculate legend position and domain_bottom
    # Order from bottom (y=0) to top (y=1): notes -> legend -> X-axis title -> plot area
    # In Plotly paper coordinates, y=0 is bottom, y=1 is top
    if has_legend:
        if notes_to_render:
            # Notes end at note_margin_frac from bottom
            # Legend positioned above notes
            legend_y_frac = note_margin_frac + legend_spacing_frac + spacing_frac["xl"] * 2
        else:
            # No notes, legend positioned accounting for X-axis title space
            legend_y_frac = xlabel_spacing_frac + legend_spacing_frac + spacing_frac["xl"] * 2
        
        # Domain ends above legend + X-axis title space
        # X-axis title extends below domain by xlabel_spacing_frac
        # So domain should end at: legend_y_frac + legend_height + xlabel_spacing_frac
        # Estimate legend height as spacing_frac["xl"] (approximate)
        legend_height_approx = spacing_frac["xl"]
        domain_bottom_frac = legend_y_frac + legend_height_approx + xlabel_spacing_frac
    else:
        # No legend, just account for X-axis title
        domain_bottom_frac = xlabel_spacing_frac
        legend_y_frac = None
    
    # Reserve vertical space for title/subtitle (top) and X-axis/legend/notes (bottom)
    # by constraining the y-axis domain to live strictly between these bands.
    domain_bottom = max(min(domain_bottom_frac, 0.9), 0.0)
    domain_top = max(min(y_top, 1.0), domain_bottom + 0.05)
    layout_updates["yaxis"]["domain"] = [domain_bottom, domain_top]

    # Choropleth maps use geo, not xaxis/yaxis; set geo.domain so the map sits in the content band
    if has_choropleth:
        try:
            geo_dict = dict(fig.layout.geo) if hasattr(fig.layout, "geo") and fig.layout.geo is not None else {}
        except Exception:
            geo_dict = {}
        layout_updates["geo"] = {
            **geo_dict,
            "domain": {"x": [0, 1], "y": [domain_bottom, domain_top]},
        }
    
    # Update legend styling and position (dynamic based on notes)
    # Legend appears below X-axis title and above notes
    # X-axis title extends from domain_bottom down by xlabel_spacing_frac
    # Legend should be positioned below where X-axis title ends
    if has_legend:
        # Position legend below X-axis title: domain_bottom - xlabel_spacing_frac - spacing
        # But ensure it's above notes if notes exist
        xaxis_title_bottom = domain_bottom - xlabel_spacing_frac if has_xlabel else domain_bottom
        if notes_to_render:
            # Legend should be below X-axis title but above notes
            # Use the higher of: (below X-axis) or (above notes)
            # Increase spacing to move legend lower below X-axis title
            legend_y = max(
                xaxis_title_bottom - legend_spacing_frac - spacing_frac["xl"] * 5,  # Below X-axis title (even more spacing)
                note_margin_frac + legend_spacing_frac  # Above notes
            )
        else:
            # No notes, position directly below X-axis title with more spacing
            legend_y = xaxis_title_bottom - legend_spacing_frac - spacing_frac["xl"] * 5 if has_xlabel else legend_spacing_frac
        
        legend_config = {
            "orientation": "h",
            "yanchor": "bottom",
            "y": legend_y,
            "xanchor": "left",  # Left-align with titles and notes
            "x": margin_x_frac,  # Use same x position as titles/notes
            "font": {"size": font_sizes["s"], "color": "#111111"},
            "itemclick": False,
            "itemdoubleclick": False,
            # Use fully transparent RGBA for no visible border.
            "bordercolor": "rgba(0,0,0,0)",
        }
        
        # Add legend title with specified styling: size s, weight semibold
        # (Plotly does not support line-height for legend title; use size s and semibold)
        if legend_title:
            legend_config["title"] = {
                "text": legend_title,
                "font": {
                    "size": font_sizes["s"],
                    "color": "#111111",
                    "weight": 600,  # semibold
                    "family": f"{font_family_name}, sans-serif",
                }
            }
        
        layout_updates["legend"] = legend_config
    
    # For line charts with temporal X-axis: move Y-axis title to top (underneath subtitle, horizontal)
    # Use the Y-axis title we captured early (right after user function)
    yaxis_title_text = yaxis_title_text_early if is_line_chart_with_temporal_x else None
    
    # Add Y-axis title as annotation at top if it exists
    if yaxis_title_text:
            # Estimate height for Y-axis title annotation
            yaxis_title_height_frac = estimate_text_height_frac(yaxis_title_text, font_sizes["s"], height)
            annotations.append({
                "text": yaxis_title_text,
                "showarrow": False,
                "xref": "paper",
                "yref": "paper",
                "x": margin_x_frac,
                "y": y_top,
                "xanchor": "left",
                "yanchor": "top",
                "font": {
                    "size": font_sizes["s"],
                    "color": "#111111",
                    "family": f"{font_family_name}, sans-serif",
                    "weight": 600,  # semibold to match Matplotlib
                },
            })
            # Adjust y_top to account for Y-axis title
            y_top -= yaxis_title_height_frac + spacing_frac["s"]
    
    # Set annotations
    layout_updates["annotations"] = annotations

    fig.update_layout(**layout_updates)

    # Apply default text font to traces that show data labels (e.g. bar charts)
    # so labels use the theme font size instead of Plotly's default; bar value labels are bold
    default_text_font = {
        "size": font_sizes["s"],
        "color": "#111111",
        "family": f"{font_family_name}, sans-serif",
    }
    bar_text_font = {**default_text_font, "weight": "bold"}
    for trace in fig.data:
        if getattr(trace, "text", None) is not None or getattr(trace, "texttemplate", None) is not None:
            font = bar_text_font if getattr(trace, "type", None) == "bar" else default_text_font
            if getattr(trace, "insidetextfont", None) is None or trace.insidetextfont == {}:
                trace.insidetextfont = font.copy()
            if getattr(trace, "outsidetextfont", None) is None or trace.outsidetextfont == {}:
                trace.outsidetextfont = font.copy()
            if getattr(trace, "textfont", None) is None or trace.textfont == {}:
                trace.textfont = font.copy()

    # Apply custom hovertemplate per World Bank style guide when not set by user.
    # Use customdata so numbers show with 2 decimals and strings show as-is (avoid NaN for categories).
    x_title = existing_xaxis_title or "X"
    y_title = yaxis_title_text_early or (yaxis_title_text if is_line_chart_with_temporal_x else None) or existing_yaxis_title or "Y"

    def _hover_fmt(val):
        if isinstance(val, (int, float)) and not np.isnan(val):
            return str(int(val)) if val == int(val) else str(round(val, 2))
        return str(val) if val is not None else ""

    for trace in fig.data:
        if getattr(trace, "hovertemplate", None) is None and getattr(
            trace, "x", None
        ) is not None and getattr(trace, "y", None) is not None:
            x_vals = list(trace.x) if hasattr(trace.x, "__iter__") and not isinstance(trace.x, str) else [trace.x]
            y_vals = list(trace.y) if hasattr(trace.y, "__iter__") and not isinstance(trace.y, str) else [trace.y]
            trace.customdata = [[_hover_fmt(x), _hover_fmt(y)] for x, y in zip(x_vals, y_vals)]
            separator_line = "_" * 30
            trace.hovertemplate = (
                f"{x_title}: <b>%{{customdata[0]}}</b><br>"
                f"{separator_line}<br>"
                f"{y_title}: <b>%{{customdata[1]}}</b>"
                "<extra></extra>"
            )

    # Zero line along the value axis: for bar charts use the axis bars extend along (x for horizontal, y for vertical);
    # for line/scatter etc. always show y-axis zeroline (linear scale)
    zeroline_style = dict(zeroline=True, zerolinewidth=1, zerolinecolor="#8A969F")
    if has_bar:
        if is_bar_chart_horizontal:
            fig.update_layout(xaxis=zeroline_style)
        else:
            fig.update_layout(yaxis=zeroline_style)
    else:
        fig.update_layout(yaxis=zeroline_style)

    # Bar charts: categorical axis tick labels uppercase and bold
    if has_bar:
        bar_trace = next((t for t in fig.data if getattr(t, "type", None) == "bar"), None)
        if bar_trace is not None:
            if is_bar_chart_horizontal:
                cat_vals = bar_trace.y
            else:
                cat_vals = bar_trace.x
            if cat_vals is not None:
                categories = list(cat_vals) if hasattr(cat_vals, "__iter__") and not isinstance(cat_vals, str) else [cat_vals]
                ticktext = [str(c).upper() for c in categories]
                cat_tickfont = {"size": font_sizes["s"], "color": "#666666", "weight": "bold"}
                if is_bar_chart_horizontal:
                    fig.update_layout(yaxis=dict(tickvals=categories, ticktext=ticktext, tickfont=cat_tickfont))
                else:
                    fig.update_layout(xaxis=dict(tickvals=categories, ticktext=ticktext, tickfont=cat_tickfont))

    # Save; rely on the caller / environment to display the returned figure.
    # Most notebook/IDE environments auto-render a returned Plotly Figure,
    # and in scripts users can call `fig.show()` explicitly.
    if save_path:
        fig.write_html(save_path)

    return fig
