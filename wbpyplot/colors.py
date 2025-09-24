# colors.py
import re
from cycler import cycler
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
    # categorical text (for annotations)
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
    # WB region colors (label map)
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
    # WB region text colors (annotation text only)
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

    # Sequential palettes (DICT but should be treated as SEQUENCE)
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

    # Diverging palettes (DICT but should be treated as SEQUENCE)
    "wb_div_default": {
        # negative → mid → positive (explicit order used in resolver)
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
}

# -----------------------------------------------------------------------------
# 2) Companion Text Aliases (annotation-only)
# -----------------------------------------------------------------------------
COMPANION_TEXT_ALIASES = {
    "wb_region": "wb_region_text",
    "wb_categorical": "wb_categorical_text",
}

# -----------------------------------------------------------------------------
# 3) Heuristics & Helpers
# -----------------------------------------------------------------------------
_num_suffix = re.compile(r".*?(\d+)$")

def _is_hex_color(s): 
    return isinstance(s, str) and s.startswith("#") and (len(s) in (4, 7))

def _looks_like_label_map(d: dict) -> bool:
    """Dict whose values are hex colors and keys are NOT gradient-like."""
    if not (isinstance(d, dict) and d):
        return False
    if not all(_is_hex_color(v) for v in d.values()):
        return False
    keys = [str(k).lower() for k in d.keys()]
    # If ALL keys look like seq*/div* → it's a gradient dict, not a label map
    if keys and all(k.startswith(("seq", "seqrev", "div")) for k in keys):
        return False
    return True

def _dict_is_gradient(d: dict) -> bool:
    """True if keys are clearly sequential/diverging tokens."""
    if not isinstance(d, dict) or not d:
        return False
    keys = [str(k).lower() for k in d.keys()]
    return keys and all(k.startswith(("seq", "seqrev", "div")) for k in keys)

def _natural_key(k: str):
    m = _num_suffix.match(k)
    if m:
        return (re.sub(r"\d+$", "", k), int(m.group(1)))
    return (k, -1)

def _derive_sequence_from_dict(name: str, d: dict[str, str]) -> list[str]:
    """Turn gradient dict into an ordered list of hex colors."""
    # Explicit diverging orders (neg → mid → pos)
    if name == "wb_div_default":
        order = ["divNeg3","divNeg2","divNeg1","divMid","divPos1","divPos2","divPos3"]
        return [d[k] for k in order if k in d]
    if name == "wb_div_alt":
        order = ["div3L3","div3L2","div3L1","div3Mid","div3R1","div3R2","div3R3"]
        return [d[k] for k in order if k in d]
    # Sequential: sort naturally by numeric suffix where present
    try:
        keys = sorted(d.keys(), key=_natural_key)
        return [d[k] for k in keys]
    except Exception:
        return list(d.values())

def _resolve_from_registry(palette: str):
    """Return ('sequence'|'label_map', node) or None."""
    if not isinstance(palette, str) or not PALETTES:
        return None
    node = PALETTES.get(palette)
    if node is None:
        return None
    if isinstance(node, dict):
        # Decide sequence vs label_map based on keys or palette name
        if _dict_is_gradient(node) or ("seq" in palette or "div" in palette):
            return ("sequence", _derive_sequence_from_dict(palette, node))
        if _looks_like_label_map(node):
            return ("label_map", dict(node))
        # Fallback: treat as sequence of values
        return ("sequence", list(node.values()))
    # If someone registers a list/tuple of hex colors
    if isinstance(node, (list, tuple)) and all(_is_hex_color(v) for v in node):
        return ("sequence", list(node))
    return None

# -----------------------------------------------------------------------------
# 4) Public resolver (returns 4-tuple)
# -----------------------------------------------------------------------------
def resolve_color_cycle_and_label_map(
    palette=None,
    n=None,
):
    """
    Returns (cycle_or_None, label_map_or_None, text_map_or_None, cmap_or_None).

    - Label-map palettes -> (None, label_map, maybe_text_map, None)
    - Sequence palettes -> (cycler, None, None, maybe_cmap)
      If name contains 'seq' or 'div' (or keys look gradient-like),
      a Colormap object is BUILT and returned (no global registration).
    """
    reg = _resolve_from_registry(palette) if isinstance(palette, str) else None
    if reg is None:
        return None, None, None, None

    kind, node = reg

    # Build a local Colormap object for gradient palettes
    cmap = None
    if isinstance(palette, str) and ("seq" in palette or "div" in palette):
        try:
            seq = list(node)  # node is a list of hex colors for sequences
            cmap = mcolors.LinearSegmentedColormap.from_list(palette, seq, N=256)
        except Exception:
            cmap = None

    if kind == "sequence":
        seq = list(node)
        if n is not None:
            seq = seq[: int(n)]
        return cycler(color=seq), None, None, cmap

    if kind == "label_map":
        text_map = None
        comp_key = COMPANION_TEXT_ALIASES.get(palette)
        if comp_key and comp_key in PALETTES and isinstance(PALETTES[comp_key], dict):
            text_map = dict(PALETTES[comp_key])
        return None, node, text_map, None

    return None, None, None, None

# -----------------------------------------------------------------------------
# 5) Application helpers
# -----------------------------------------------------------------------------
def apply_color_map_to_axes(axs, label_map: dict[str, str]) -> None:
    """Recolor artists on Axes based on label → color mapping."""
    for ax in axs:
        # Lines
        for line in ax.get_lines():
            lbl = line.get_label()
            if lbl in label_map:
                line.set_color(label_map[lbl])
        # Patches (bars, wedges, etc.)
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
    """Color ONLY annotation text (ax.text), not legend text."""
    for ax in axs:
        for t in ax.texts:
            txt = t.get_text()
            if txt in text_map:
                try:
                    t.set_color(text_map[txt])
                except Exception:
                    pass

def apply_legend_marker_colors(axs, label_map: dict[str, str]) -> None:
    """Ensure legend markers reflect the main palette; legend text unchanged."""
    from matplotlib.lines import Line2D
    from matplotlib.collections import PathCollection
    from matplotlib.patches import Patch

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
                    try: h.set_color(c)
                    except Exception: pass
            elif isinstance(h, Patch):
                h.set_facecolor(c)
                h.set_edgecolor(c)
