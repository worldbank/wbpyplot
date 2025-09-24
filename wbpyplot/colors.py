import numpy as np
from cycler import cycler
from pypalettes import create_cmap
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
    "wb_region_secondary": {
        "NAC1": "#80d2e8",
        "NAC2": "#163c6c",
        "NAC3": "#106ca1",
        "SSF1": "#ffd554",
        "SSF2": "#8f3b18",
        "SSF3": "#c2660d",
        "MEA1": "#b38fd8",
        "MEA2": "#462f98",
        "MEA3": "#edc2f1",
        "SAS1": "#228b8b",
        "SAS2": "#006061",
        "SAS3": "#95e2e2",
        "EAS1": "#f8a8df",
        "EAS2": "#bb3b64",
        "EAS3": "#801e37",
        "LCN1": "#54ae89",
        "LCN2": "#084d31",
        "LCN3": "#9adeaa",
        "ECS1": "#eb6e51",
        "ECS2": "#ff9e75",
        "ECS3": "#d43729",
        "AFW1": "#7b7c13",
        "AFW2": "#abaa22",
        "AFW3": "#4e5200",
        "AFE1": "#ffd554",
        "AFE2": "#8f3b18",
        "AFE3": "#c2660d",
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
    "wb_income": {
        # WB income group colors
        "HIC": "#016B6C",
        "UMC": "#73AF48",
        "LMC": "#DB95D7",
        "LIC": "#3B4DA6",
    }, 
    "wb_gender": {
        # WB gender group colors
        "male": "#664AB6",
        "female": "#FF9800",
        "diverse": "#4EC2C0",
    }, 
    "wb_urbanisation": {
        # WB urbanisation colors
        "rural": "#54AE89",
        "urban": "#6D88D1",
    }, 
    "wb_age": {
        # WB age group colors
        # Use the age group colors consistently across different age disaggregations. Youngest should be used for all age groups describing babies & toddlers, younger for age groups describing kids (school age), middle for younger adults, older for older adults and oldest for seniors.
        "youngestAge": "#F8A8DF",
        "youngerAge": "#B38FD8",
        "middleAge": "#462f98",
        "olderAge": "#6D88D1",
        "oldestAge": "#A1C6FF",
    },
    "wb_binary": {
        # WB binary colors
        "yes": "#0071BC",
        "no": "#EBEEF4",
    }, 
    "wb_total": {
    # WB total color
    # When showing disaggregations together with a total, use total color for showing the total values.
        "total": "#163C6C",
    },
    "wb_reference": {
    # To show a regional or global benchmark or a reference country to compare against another selected country, use the reference color.
        "reference": "#8A969F",
    }, 
    "wb_noData": {
    # For representations such as maps that contain countries without data, use the color for noData.
        "noData": "#CED4DE",
    },
    "wb_highlight_selection": {
    # To highlight a country across multiple charts, use one of the two selection colors.
        "selection1": "#0071BC",
	    "selection2": "#8963C1",
    },
    "wb_text_colors":{
    # The two label colors can be used for emphasized (dark) and subtle (light) text in charts. Dark text should be used for instance in tooltips for data values or for axis labels. Light text can be used for secondary information such as axis or legend tick labels and units.
        "text": "#111111",
        "textSubtle": "#666666",
    },
    "wb_greys": {
    # Please refer to the Chart Elements page to see which grey to use for which chart element specifically.
        "grey500": "#111111",
        "grey400": "#666666",
        "grey300": "#8a969f",
        "grey200": "#CED4DE",
        "grey100": "#EBEEF4",
    },
    # WB sequence - bad to good.
    # This color scale works best when larger numbers signify more favorable conditions (e.g. labor force participation rate, access to electricity, GDP per capita).
    "wb_seq_bad_to_good":{
        "seq1": "#FDF6DB",
        "seq2": "#A1CBCF",
        "seq3": "#5D99C2",
        "seq4": "#2868A0",
        "seq5": "#023B6F",
    },
    # WB sequence - good to bad. 
    # This color scale works best when larger numbers signify less favorable conditions (e.g. poverty rate, GHG emissions, prevalence of stunting).
    "wb_seq_good_to_bad": {
        "seqRev1": "#E3F6FD",
        "seqRev2": "#91C5F0",
        "seqRev3": "#8B8AC0",
        "seqRev4": "#88506E",
        "seqRev5": "#691B15",
    },
    # WB sequence - monochrome blue.
    "wb_seq_monochrome_blue": {
        "seqB1": "#E3F6FD",
        "seqB2": "#75CCEC",
        "seqB3": "#089BD4",
        "seqB4": "#0169A1",
        "seqB5": "#023B6F",
    },
    # WB sequence - monochrome yellow.
    "wb_seq_monochrome_yellow": {
        "seqY1": "#FDF7DB",
        "seqY2": "#ECB63A",
        "seqY3": "#BE792B",
        "seqY4": "#8D4117",
        "seqY5": "#5C0000",
    },
    # WB sequence - monochrome purple.
    "wb_seq_monochrome_purple": {
        "seqP1": "#FFE2FF",
        "seqP2": "#D3ACE6",
        "seqP3": "#A37ACD",
        "seqP4": "#6F4CB4",
        "seqP5": "#2F1E9C",
    },
    # WB sequence - monochrome green.
    "wb_seq_monochrome_green": {
        "seqG1": "#d2ffe1",
        "seqG2": "#8ad4a7",
        "seqG3": "#54a67f",
        "seqG4": "#27795a",
        "seqG5": "#084d31",
    },
    # WB sequence - monochrome red
    "wb_seq_monochrome_red": {
        "seqR1": "#ffd6b9",
        "seqR2": "#f99c78",
        "seqR3": "#e56245",
        "seqR4": "#c1261a",
        "seqR5": "#870000",
    },
    # WB diverging - default
    # This diverging scale works best when showing numbers with a connotation of good/bad for higher or lower values (e.g. GDP growth). Use the warmer shades for the numbers with the more negative connotation and the cooler shades to show positive values.
    "wb_div_default": {
        "divPos3": "#025288",
        "divPos2": "#3587C3",
        "divPos1": "#80BDE7",
        "divMid": "#EFEFEF",
        "divNeg1": "#E3A763",
        "divNeg2": "#BD6126",
        "divNeg3": "#920000",
    },
    # WB diverging - neutral
    # This diverging scale was designed to work well in conditions when showing numbers without a clear connotation of good/bad for higher or lower values (e.g. growth in urban vs rural living).
    "wb_div_neutral": {
        "div2L3": "#24768E",
        "div2L2": "#4EA2AC",
        "div2L1": "#98CBCC",
        "div2Mid": "#EFEFEF",
        "div2R1": "#D1AEE3",
        "div2R2": "#A873C4",
        "div2R3": "#754493",
    },
    # WB diverging - alternative 
    # This diverging scale can be used as an alternative for the Default diverging scale if you want to emphasize the negative connotation of the numbers more strongly.
    "wb_div_alt": {
        "div3L3": "#002c8b",
        "div3L2": "#4868af",
        "div3L1": "#79a7d5",
        "div3Mid": "#efefef",
        "div3R1": "#eca08c",
        "div3R2": "#c9573e",
        "div3R3": "#920000",
    },
    # These colors should be used with caution in visualizations. They are not tested for sufficient background contrast and should not be used together in the same chart (e.g. to distinguish categories).
    "wb_pillars": {
        "people": "#f7b841",
        "planet": "#07ab50",
        "prosperity": "#872c8f",
        "infrastructure": "#91302f",
        "digital": "#5d6472",
        "corporate": "#004972"
    },
}
     
   

COMPANION_TEXT_ALIASES = {
    "wb_region": "wb_region_text",
    "wb_categorical": "wb_categorical_text",
}

# Which palettes are *forced* into label-map vs cycle behavior
LABEL_MAP_ONLY = {
    "wb_region",
    "wb_region_secondary",
    "wb_age", 
    "wb_gender",
    "wb_income", 
    "wb_binary",
    "wb_total", 
    "wb_pillars"
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

def register_label_map_palette(name: str) -> None:
    LABEL_MAP_ONLY.add(name)

def register_cycle_palette(name: str) -> None:
    AUTO_CYCLE_ONLY.add(name)

# ---------------------------------------------------------------------------
# 3) Registry resolution helpers
# ---------------------------------------------------------------------------
def resolve_palette_alias(name: str) -> str | None:
    return PALETTE_ALIASES.get(name)

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
    alias_path = resolve_palette_alias(palette)
    if alias_path:
        node = _get_by_path(PALETTES, alias_path)
        if node is None:
            raise KeyError(f"Alias '{palette}' points to missing path '{alias_path}'")
        if _looks_like_sequence(node): return ("sequence", list(node))
        if _looks_like_label_map(node): return ("label_map", dict(node))
    node = _get_by_path(PALETTES, palette)
    if node is not None:
        if _looks_like_sequence(node): return ("sequence", list(node))
        if _looks_like_label_map(node): return ("label_map", dict(node))
    node = _search_first_match(PALETTES, palette)
    if node is not None:
        if _looks_like_sequence(node): return ("sequence", list(node))
        if _looks_like_label_map(node): return ("label_map", dict(node))
    return None

# ---------------------------------------------------------------------------
# 4) Public resolver
# ---------------------------------------------------------------------------
def resolve_color_cycle_and_label_map(
    palette=None,
    palettes=None,
    n=None,
    palette_kwargs=None,
):
    """
    Returns (cycler_or_None, label_map_or_None, text_map_or_None).
    - cycle palettes: auto-cycle regardless of labels
    - label_map palettes: recolor by label
    - companion text maps: only applied to annotations
    """
    palette_kwargs = palette_kwargs or {}

    def _force_mode(name: str, reg_tuple):
        base = resolve_palette_alias(name) or name
        if base in LABEL_MAP_ONLY:
            return ("label_map", reg_tuple[1]) if reg_tuple and reg_tuple[0] == "label_map" else None
        if base in AUTO_CYCLE_ONLY:
            return ("sequence", reg_tuple[1]) if reg_tuple and reg_tuple[0] == "sequence" else None
        return reg_tuple

    # --- Single palette
    reg = _resolve_from_registry(palette) if isinstance(palette, str) else None
    reg = _force_mode(palette, reg) if isinstance(palette, str) else reg

    if reg is not None:
        kind, node = reg
        if kind == "sequence":
            colors = node if n is None else node[: int(n)]
            return cycler(color=colors), None, None
        if kind == "label_map":
            text_map = None
            base_key = resolve_palette_alias(palette) or palette
            comp_key = COMPANION_TEXT_ALIASES.get(base_key)
            if comp_key:
                comp = _resolve_from_registry(comp_key)
                if comp and comp[0] == "label_map":
                    text_map = comp[1]
            return None, node, text_map

    # --- Multiple palettes (concat if all cycles)
    concat = []
    if palettes:
        items = palettes if isinstance(palettes, (list, tuple)) else [palettes]
        all_seq = True
        for p in items:
            r = _resolve_from_registry(p) if isinstance(p, str) else None
            r = _force_mode(p, r) if isinstance(p, str) else r
            if r is None or r[0] != "sequence":
                all_seq = False
                break
            concat.extend(r[1])
        if all_seq and concat:
            if n is not None:
                concat = concat[: int(n)]
            return cycler(color=concat), None, None

    # --- Fallback: pypalettes.create_cmap
    cmap = None
    if create_cmap is not None:
        sources = []
        if palettes is not None:
            sources.extend(items if 'items' in locals() else (palettes if isinstance(palettes, (list, tuple)) else [palettes]))
        if palette is not None:
            sources.append(palette)
        if sources:
            cmap = create_cmap(palettes=sources, **palette_kwargs)
    if cmap is not None:
        k = int(n) if n is not None else 10
        if hasattr(cmap, "colors"):
            colors = list(cmap.colors)[:k]
        else:
            xs = np.linspace(0, 1, k)
            colors = [cmap(x) for x in xs]
        return cycler(color=colors), None, None

    return None, None, None

# ---------------------------------------------------------------------------
# 5) Application helpers
# ---------------------------------------------------------------------------
def apply_color_map_to_axes(axs, label_map: dict[str, str]) -> None:
    """Recolor artists on Axes based on label → color mapping."""
    for ax in axs:
        for line in ax.get_lines():
            lbl = line.get_label()
            if lbl in label_map:
                line.set_color(label_map[lbl])
        for patch in ax.patches:
            lbl = patch.get_label()
            if lbl in label_map:
                patch.set_facecolor(label_map[lbl])
        for coll in ax.collections:
            lbl = coll.get_label()
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
    """Ensure legend markers reflect the main palette, not legend text."""
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
