import numpy as np
from cycler import cycler
from pypalettes import create_cmap
import matplotlib.colors as mcolors

# -----------------------------------------------------------------------------
# 1) Palette Registry
# -----------------------------------------------------------------------------
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
    # Diverging example
    "wb_div_default": {
        "divPos3": "#025288",
        "divPos2": "#3587C3",
        "divPos1": "#80BDE7",
        "divMid": "#EFEFEF",
        "divNeg1": "#E3A763",
        "divNeg2": "#BD6126",
        "divNeg3": "#920000",
    },
}

# -----------------------------------------------------------------------------
# 2) Companion Text Aliases
# -----------------------------------------------------------------------------
COMPANION_TEXT_ALIASES = {
    "wb_region": "wb_region_text",
    "wb_categorical": "wb_categorical_text",
}

# -----------------------------------------------------------------------------
# 3) Forced Modes
# -----------------------------------------------------------------------------
LABEL_MAP_ONLY = {
    "wb_region",
}
AUTO_CYCLE_ONLY = {
    "wb_categorical",
    "wb_categorical_text",
    "wb_region_text",
}

# -----------------------------------------------------------------------------
# 4) Helpers
# -----------------------------------------------------------------------------
def _is_hex_color(s): return isinstance(s, str) and s.startswith("#") and (len(s) in (4, 7))
def _looks_like_label_map(d): return isinstance(d, dict) and d and all(_is_hex_color(v) for v in d.values())
def _looks_like_sequence(x): return isinstance(x, (list, tuple)) and x and all(_is_hex_color(v) for v in x)

def _get_by_path(root, dotted):
    node = root
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node

def _search_first_match(root, key):
    if not isinstance(root, dict):
        return None
    if key in root:
        return root[key]
    for v in root.values():
        if isinstance(v, dict):
            found = _search_first_match(v, key)
            if found is not None:
                return found
    return None

def _resolve_from_registry(palette):
    if not isinstance(palette, str) or not PALETTES:
        return None
    node = _get_by_path(PALETTES, palette)
    if node is not None:
        if _looks_like_sequence(node): return ("sequence", list(node))
        if _looks_like_label_map(node): return ("label_map", dict(node))
    node = _search_first_match(PALETTES, palette)
    if node is not None:
        if _looks_like_sequence(node): return ("sequence", list(node))
        if _looks_like_label_map(node): return ("label_map", dict(node))
    return None

def _derive_sequence_from_dict(name, dct):
    """Turn dict of hex colors into a consistent ordered list."""
    return list(dct.values())

# -----------------------------------------------------------------------------
# 5) Resolver
# -----------------------------------------------------------------------------
def resolve_color_cycle_and_label_map(
    palette=None,
    palettes=None,
    n=None
):
    """
    Returns (cycler_or_None, label_map_or_None, text_map_or_None, cmap_or_None).
    """
    reg = _resolve_from_registry(palette) if isinstance(palette, str) else None
    if reg is None:
        return None, None, None, None

    kind, node = reg
    cmap = None

    if isinstance(palette, str) and ("seq" in palette or "div" in palette):
        seq = _derive_sequence_from_dict(palette, node) if isinstance(node, dict) else list(node)
        cmap = mcolors.LinearSegmentedColormap.from_list(palette, seq, N=256)

    if kind == "sequence":
        colors = node if isinstance(node, list) else list(node)
        if n is not None:
            colors = colors[: int(n)]
        return cycler(color=colors), None, None, cmap

    if kind == "label_map":
        text_map = None
        comp_key = COMPANION_TEXT_ALIASES.get(palette)
        if comp_key:
            comp = _resolve_from_registry(comp_key)
            if comp and comp[0] == "label_map":
                text_map = comp[1]
        return None, node, text_map, None

    return None, None, None, None

# -----------------------------------------------------------------------------
# 6) Application helpers
# -----------------------------------------------------------------------------
def apply_cmap_to_mappables(axs, cmap):
    if cmap is None:
        return
    for ax in axs:
        for im in getattr(ax, "images", []):
            try: im.set_cmap(cmap)
            except Exception: pass
        for coll in ax.collections:
            if hasattr(coll, "set_cmap"):
                try: coll.set_cmap(cmap)
                except Exception: pass

def apply_color_map_to_axes(axs, label_map: dict[str, str]) -> None:
    for ax in axs:
        for line in ax.get_lines():
            if line.get_label() in label_map:
                line.set_color(label_map[line.get_label()])
        for patch in ax.patches:
            if patch.get_label() in label_map:
                patch.set_facecolor(label_map[patch.get_label()])
        for coll in ax.collections:
            if coll.get_label() in label_map:
                try: coll.set_facecolor(label_map[coll.get_label()])
                except Exception: pass

def apply_annotation_text_colors(axs, text_map: dict[str, str]) -> None:
    for ax in axs:
        for t in ax.texts:
            if t.get_text() in text_map:
                try: t.set_color(text_map[t.get_text()])
                except Exception: pass

def apply_legend_marker_colors(axs, label_map: dict[str, str]) -> None:
    from matplotlib.lines import Line2D
    from matplotlib.collections import PathCollection
    from matplotlib.patches import Patch

    for ax in axs:
        leg = ax.get_legend()
        if leg is None: continue
        for h, txt in zip(leg.legendHandles, leg.texts):
            name = txt.get_text()
            c = label_map.get(name)
            if c is None: continue
            if isinstance(h, Line2D):
                h.set_color(c)
                h.set_markerfacecolor(c)
                h.set_markeredgecolor(c)
            elif isinstance(h, PathCollection):
                try:
                    h.set_facecolor(c)
                    h.set_edgecolor(c)
                except Exception:
                    try: h.set_color(c)
                    except Exception: pass
            elif isinstance(h, Patch):
                h.set_facecolor(c)
                h.set_edgecolor(c)
