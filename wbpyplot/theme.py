import os
from matplotlib import font_manager
import matplotlib.pyplot as plt

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

def set_font_family(file):
    font_file = os.path.join(PACKAGE_DIR, "fonts", file)
    if not os.path.isfile(font_file):
        raise ValueError(f"Font not found: {font_file}")
    font_prop = font_manager.FontProperties(fname=font_file)
    font_manager.fontManager.addfont(font_file)
    return font_prop.get_name()


wb_rcparams = {
    "font.family": set_font_family("OpenSans.ttf"),
    "axes.titleweight": "bold",
    "axes.edgecolor": "none",
    "axes.grid": True,
    "grid.color": "#CED4DE",  # grey200 per style guide
    "grid.linestyle": (0, (4, 2)),  # dash 4 2 per style guide
    "grid.linewidth": 1,  # 1px per style guide
    "xtick.direction": "out",
    "ytick.direction": "out",
    "legend.frameon": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "lines.linewidth": 2.0,
    "lines.markersize": 6,
    "axes.prop_cycle": plt.cycler(
        color=[
            "#34A7F2",
            "#FF9800",
            "#664AB6",
            "#4EC2C0",
            "#F3578E",
            "#081079",
            "#0C7C68",
            "#AA0000",
            "#DDDA21",
        ]
    ),
}


def get_dynamic_sizes(width):
    # Sizes tuned so text doesn't dominate the plot area when embedded (e.g. Quarto)
    if width < 400:
        font_sizes = {"s": 10, "m": 12, "l": 14}
        spacing = {"xxs": 2, "xs": 4, "s": 5, "m": 10, "l": 12, "xl": 14}
    elif 400 <= width <= 700:
        font_sizes = {"s": 11, "m": 13, "l": 15}
        spacing = {"xxs": 2, "xs": 5, "s": 7, "m": 11, "l": 14, "xl": 17}
    else:
        font_sizes = {"s": 12, "m": 14, "l": 17}
        spacing = {"xxs": 3, "xs": 6, "s": 9, "m": 13, "l": 16, "xl": 20}
    return font_sizes, spacing
