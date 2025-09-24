# colors.py
import numpy as np
import matplotlib.colors as mcolors
from cycler import cycler
from matplotlib.lines import Line2D
from matplotlib.collections import PathCollection
from matplotlib.patches import Patch

PALETTES = {
    # categorical colors
    "wb_categorical": {
        "cat1": "#34A7F2",
        "cat2": "#FF9800",
        "cat3": "#664AB6",
        "cat4": "#4EC2C0",
        "cat5": "#F3578E",
        "cat6": "#081079",
        "cat7": "#0C7C68",
        "cat8": "#AA0000",
        "cat9": "#DDDA21",
    },
    # categorical text
    "wb_categorical_text": {
        "cat1Text": "#106CA1",
        "cat2Text": "#B65F0C",
        "cat3Text": "#664AB6",
        "cat4Text": "#208383",
        "cat5Text": "#BB3B64",
        "cat6Text": "#081079",
        "cat7Text": "#0C7C68",
        "cat8Text": "#AA0000",
        "cat9Text": "#767712",
    },
    # WB region colors
    "wb_region": {
        "WLD": "#081079",
        "NAC": "#34A7F2",
        "LCN": "#0C7C68",
        "SAS": "#4EC2C0",
        "MEA": "#664AB6",
        "ECS": "#AA0000",
        "EAS": "#F3578E",
        "SSF": "#FF9800",
        "AFE": "#FF9800",
        "AFW": "#DDDA21",
    },
    # WB region text colors
    "wb_region_text": {
        "NACText": "#106CA1",
        "SSFText": "#B65F0C",
        "AFEText": "#B65F0C",
        "MEAText": "#664AB6",
        "SASText": "#208383",
        "EASText": "#BB3B64",
        "WLDText": "#081079",
        "LCNText": "#0C7C68",
        "ECSText": "#AA0000",
        "AFWText": "#767712",
    },

    # Sequential palettes
    "wb_seq_bad_to_good": {
        "seq1": "#FDF6DB",
        "seq2": "#A1CBCF",
        "seq3": "#5D99C2",
        "seq4": "#2868A0",
        "seq5": "#023B6F",
    },
    "wb_seq_good_to_bad": {
        "seqRev1": "#E3F6FD",
        "seqRev2": "#91C5F0",
        "seqRev3": "#8B8AC0",
        "seqRev4": "#88506E",
        "seqRev5": "#691B15",
    },

    # Diverging palettes
    "wb_div_default": {
        "divNeg3": "#920000",
        "divNeg2": "#BD6126",
        "divNeg1": "#E3A763",
        "divMid":  "#EFEFEF",
        "divPos1": "#80BDE7",
        "divPos2": "#3587C3",
        "divPos3": "#025288",
    },
    "wb_div_alt": {
        "div3L3": "#002c8b",
        "div3L2": "#4868af",
        "div3L1": "#79a7d5",
        "div3Mid": "#efefef",
        "div3R1": "#eca08c",
        "div3R2": "#c9573e",
        "div3R3": "#920000",
    },

    # Extras / groups
    "wb_income": {"HIC": "#016B6C", "UMC": "#73AF48", "LMC": "#DB95D7", "LIC": "#3B4DA6"},
    "wb_gender": {"male": "#664AB6", "female": "#FF9800", "diverse": "#4EC2C0"},
    "wb_urbanisation": {"rural": "#54AE89", "urban": "#6D88D1"},
    "wb_age": {
        "youngestAge": "#F8A8DF",
        "youngerAge": "#B38FD8",
        "middleAge": "#462f98",
        "olderAge": "#6D88D1",
        "oldestAge": "#A1C6FF",
    },
    "wb_binary": {"yes": "#0071BC", "no": "#EBEEF4"},
    "wb_total": {"total": "#163C6C"},
    "wb_reference": {"reference": "#8A969F"},
    "wb_noData": {"noData": "#CED4DE"},
    "wb_highlight_selection": {"selection1": "#0071BC", "selection2": "#8963C1"},
    "wb_text_colors": {"text": "#111111", "textSubtle": "#666666"},
    "wb_greys": {
        "grey500": "#111111",
        "grey400": "#666666",
        "grey300": "#8a969f",
        "grey200": "#CED4DE",
        "grey100": "#EBEEF4",
    },
    "wb_seq_monochrome_blue": {
        "seqB1": "#E3F6FD",
        "seqB2": "#75CCEC",
        "seqB3": "#089BD4",
        "seqB4": "#0169A1",
        "seqB5": "#023B6F",
    },
    "wb_seq_monochrome_yellow": {
        "seqY1": "#FDF7DB",
        "seqY2": "#ECB63A",
        "seqY3": "#BE792B",
        "seqY4": "#8D4117",
        "seqY5": "#5C0000",
    },
    "wb_seq_monochrome_purple": {
        "seqP1": "#FFE2FF",
        "seqP2": "#D3ACE6",
        "seqP3": "#A37ACD",
        "seqP4": "#6F4CB4",
        "seqP5": "#2F1E9C",
    },
    "wb_seq_monochrome_green": {
        "seqG1": "#d2ffe1",
        "seqG2": "#8ad4a7",
        "seqG3": "#54a67f",
        "seqG4": "#27795a",
        "seqG5": "#084d31",
    },
    "wb_seq_monochrome_red": {
        "seqR1": "#ffd6b9",
        "seqR2": "#f99c78",
        "seqR3": "#e56245",
        "seqR4": "#c1261a",
        "seqR5": "#870000",
    },
    "wb_div_neutral": {
        "div2L3": "#24768E",
        "div2L2": "#4EA2AC",
        "div2L1": "#98CBCC",
        "div2Mid": "#EFEFEF",
        "div2R1": "#D1AEE3",
        "div2R2": "#A873C4",
        "div2R3": "#754493",
    },
    "wb_pillars": {
        "people": "#f7b841",
        "planet": "#07ab50",
        "prosperity": "#872c8f",
        "infrastructure": "#91302f",
        "digital": "#5d6472",
        "corporate": "#004972",
    },
}

COMPANION_TEXT_ALIASES = {
    "wb_region": "wb_region_text",
    "wb_categorical": "wb_categorical_text",
}

# Which palettes are forced to label-map vs cycle behavior
LABEL_MAP_ONLY = {
    "wb_region",
    "wb_region_secondary",
    "wb_age",
    "wb_gender",
    "wb_income",
    "wb_binary",
    "wb_total",
    "wb_pillars",
}
AUTO_CYCLE_ONLY = {
    "wb_categorical",
    "wb_categorical_text",
    "wb_region_text",
    "wb_reference",
    "wb_noData",
    "wb_highlight_selection",
    "wb_text_colors",
    "wb_greys",
    "wb_seq_bad_to_good",
    "wb_seq_good_to_bad",
    "wb_seq_monochrome_blue",
    "wb_seq_monochrome_green",
    "wb_seq_monochrome_red",
    "wb_seq_monochrome_yellow",
    "wb_seq_monochrome_purple",
    "wb_div_default",
    "wb_div_neutral",
    "wb_div_alt",
}

def _is_hex_color(s):
    return isinstance(s, str) and s.startswith("#") and (len(s) in (4, 7))

def _looks_like_label_map(d):
    return isinstance(d, dict) and d and all(_is_hex_color(v) for v in d.values())

def _looks_like_sequence(x):
    return isinstance(x, (list, tuple)) and x and all(_is_hex_color(v) for v in x)

def _resolve_from_registry(palette):
    if not isinstance(palette, str) or not PALETTES:
        return None
    node = PALETTES.get(palette)
    if node is None:
        return None
    if isinstance(node, dict):
        # If palette name includes seq/div, treat as sequence (gradient list via values order)
        if ("seq" in palette) or ("div" in palette):
            return ("sequence", list(node.values()))
        if _looks_like_label_map(node):
            return ("label_map", dict(node))
        return ("sequence", list(node.values()))
    if _looks_like_sequence(node):
        return ("sequence", list(node))
    return None

def resolve_color_cycle_and_label_map(
    palette=None,
    n=None,
):
    """
    Returns (cycler_or_None, label_map_or_None, text_map_or_None, cmap_or_None).
    """
    def _force_mode(name: str, reg_tuple):
        if name in LABEL_MAP_ONLY and reg_tuple and reg_tuple[0] == "label_map":
            return ("label_map", reg_tuple[1])
        if name in AUTO_CYCLE_ONLY and reg_tuple and reg_tuple[0] == "sequence":
            return ("sequence", reg_tuple[1])
        return reg_tuple

    reg = _resolve_from_registry(palette) if isinstance(palette, str) else None
    reg = _force_mode(palette, reg) if isinstance(palette, str) else reg

    if reg is None:
        return None, None, None, None

    kind, node = reg

    # Build a Colormap object for sequential/diverging palettes
    cmap = None
    if isinstance(palette, str) and ("seq" in palette or "div" in palette):
        try:
            seq = list(node)  # node is already an ordered list of hex colors
            cmap = mcolors.LinearSegmentedColormap.from_list(palette, seq, N=256)
        except Exception:
            cmap = None

    if kind == "sequence":
        colors = list(node)
        if n is not None:
            colors = colors[: int(n)]
        return cycler(color=colors), None, None, cmap

    if kind == "label_map":
        text_map = None
        comp_key = COMPANION_TEXT_ALIASES.get(palette)
        if comp_key and comp_key in PALETTES and isinstance(PALETTES[comp_key], dict):
            text_map = dict(PALETTES[comp_key])
        return None, node, text_map, None

    return None, None, None, None

def apply_color_map_to_axes(axs, label_map: dict[str, str]) -> None:
    for ax in axs:
        # Lines
        for line in ax.get_lines():
            lbl = line.get_label()
            if lbl in label_map:
                line.set_color(label_map[lbl])
        # Patches (bars, wedges)
        for patch in ax.patches:
            lbl = getattr(patch, "get_label", lambda: None)()
            if lbl in label_map:
                patch.set_facecolor(label_map[lbl])
        # Collections (scatter, etc.)
        for coll in ax.collections:
            lbl = getattr(coll, "get_label", lambda: None)()
            if lbl in label_map:
                try:
                    coll.set_facecolor(label_map[lbl])
                except Exception:
                    pass

def apply_annotation_text_colors(axs, text_map: dict[str, str]) -> None:
    for ax in axs:
        for t in ax.texts:
            txt = t.get_text()
            if txt in text_map:
                try:
                    t.set_color(text_map[txt])
                except Exception:
                    pass

def apply_legend_marker_colors(axs, label_map: dict[str, str]) -> None:
    for ax in axs:
        leg = ax.get_legend()
        if leg is None:
            continue
        for h, txt in zip(leg.legendHandles, leg.texts):
            name = txt.get_text()
            c = label_map.get(name)
            if c is None:
                continue
            if isinstance(h, Line2D):
                h.set_color(c)
                h.set_markerfacecolor(c)
                h.set_markeredgecolor(c)
            elif isinstance(h, PathCollection):
                try:
                    h.set_facecolor(c)
                    h.set_edgecolor(c)
                except Exception:
                    try:
                        h.set_color(c)
                    except Exception:
                        pass
            elif isinstance(h, Patch):
                h.set_facecolor(c)
                h.set_edgecolor(c)

# -----------------------------------------------------------------------------
# Continuous -> binned helpers + colorbar handling
# -----------------------------------------------------------------------------
def build_binned_cmap_and_norm_from_axes(axs, cmap, bins, mode="linear"):
    """
    Build (ListedColormap, BoundaryNorm) for all mappables on the given axes.
    bins : int -> number of bins (uniform/quantile)
           sequence -> explicit bin edges
    """
    arrays = []
    for ax in axs:
        # images (imshow)
        for im in getattr(ax, "images", []):
            arr = getattr(im, "get_array", lambda: None)()
            if arr is not None:
                arr = np.asarray(arr)
                if arr.size:
                    arrays.append(arr)
        # collections (pcolormesh, contourf -> QuadMesh, PolyCollection)
        for coll in ax.collections:
            arr = getattr(coll, "get_array", lambda: None)()
            if arr is not None:
                arr = np.asarray(arr)
                if arr.size:
                    arrays.append(arr)

    if not arrays:
        return None, None
    data = np.concatenate([a.ravel() for a in arrays])
    data = data[np.isfinite(data)]
    if data.size == 0:
        return None, None

    # Compute edges
    if hasattr(bins, "__iter__"):
        edges = np.asarray(list(bins), dtype=float)
        if edges.ndim != 1 or edges.size < 2:
            return None, None
        nbins = edges.size - 1
    elif isinstance(bins, int) and bins > 0:
        nbins = int(bins)
        if str(mode).lower() == "quantile":
            qs = np.linspace(0, 1, nbins + 1)
            edges = np.quantile(data, qs)
        else:  # linear
            dmin, dmax = float(np.nanmin(data)), float(np.nanmax(data))
            if not np.isfinite(dmin) or not np.isfinite(dmax) or dmin == dmax:
                return None, None
            edges = np.linspace(dmin, dmax, nbins + 1)
    else:
        return None, None

    # Sample original cmap at bin centers -> discrete colors
    centers = 0.5 * (edges[:-1] + edges[1:])
    t = (centers - centers.min()) / (centers.max() - centers.min() + 1e-12)
    colors = cmap(t)

    listed = mcolors.ListedColormap(colors, name=getattr(cmap, "name", "binned"))
    norm = mcolors.BoundaryNorm(edges, ncolors=listed.N, clip=True)
    return listed, norm

def apply_cmap_to_mappables(axs, cmap, norm=None, force_recreate_cb=True):
    """
    Apply cmap/norm to imshow/pcolormesh/contourf outputs and refresh colorbars.
    If mappable uses BoundaryNorm and a colorbar already exists, we recreate it
    to guarantee discrete rendering.
    """
    if cmap is None and norm is None:
        return

    updated = []
    for ax in axs:
        # images
        for im in getattr(ax, "images", []):
            try:
                if cmap is not None:
                    im.set_cmap(cmap)
                if norm is not None:
                    im.set_norm(norm)
                updated.append(im)
            except Exception:
                pass
        # collections (QuadMesh, PolyCollection, etc.)
        for coll in ax.collections:
            if hasattr(coll, "set_cmap"):
                try:
                    if cmap is not None:
                        coll.set_cmap(cmap)
                    if norm is not None and hasattr(coll, "set_norm"):
                        coll.set_norm(norm)
                    updated.append(coll)
                except Exception:
                    pass

    # update existing colorbars; recreate if needed for BoundaryNorm
    for m in updated:
        cb = getattr(m, "colorbar", None)  # set by fig.colorbar/plt.colorbar
        if cb is None:
            continue

        # Try updating in-place first
        try:
            cb.update_normal(m)
        except Exception:
            pass

        if not force_recreate_cb:
            continue

        # If discrete norm, rebuild the colorbar so it shows discrete patches
        mnorm = getattr(m, "norm", None)
        if isinstance(mnorm, mcolors.BoundaryNorm):
            try:
                ax = m.axes
                fig = ax.figure
                # Keep existing label, orientation, etc., as best-effort
                label = cb.ax.get_ylabel()
                orientation = getattr(cb, "orientation", "vertical")
                cb.remove()
                new_cb = fig.colorbar(m, ax=ax, orientation=orientation)
                if label:
                    new_cb.set_label(label)
            except Exception:
                # fall back to update only
                try:
                    cb.update_normal(m)
                except Exception:
                    pass
