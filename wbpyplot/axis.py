
import numpy as np

def apply_axis_styling(ax, wb_font_sizes, wb_spacing, chart_type):
    for axis in [ax.xaxis, ax.yaxis]:
        axis.label.set_fontsize(wb_font_sizes['s'])
        axis.label.set_fontweight('semibold')
        axis.label.set_color('#111111')
        axis.label.set_linespacing(1.2)

    for ticklabel in ax.get_xticklabels() + ax.get_yticklabels():
        ticklabel.set_fontsize(wb_font_sizes['s'])
        ticklabel.set_fontweight('regular')
        ticklabel.set_color('#666666')
        ticklabel.set_linespacing(1.2)

    ax.grid(True, which='major', linestyle=(0, (4, 2)), linewidth=1, color='#CED4DE')

    def add_zero_line():
        if ax.get_yscale() == 'linear':
            ax.figure.canvas.draw()
            ylim = ax.get_ylim()
            if ylim[0] <= 0 <= ylim[1]:
                ax.axhline(0, linewidth=1, color='#8A969F', zorder=5)

    if chart_type in ('scatter', 'single_numeric'):
        add_zero_line()

    if chart_type == 'scatter':
        x_pad = wb_spacing['xxs']
        y_pad = wb_spacing['xxs']
        ax.xaxis.labelpad = x_pad
        ax.yaxis.labelpad = y_pad
        for label in ax.get_xticklabels():
            label.set_y(label.get_position()[1] - 0.01)
        for label in ax.get_yticklabels():
            label.set_x(label.get_position()[0] - 0.01)

    elif chart_type == 'timeseries':
        ax.set_xlabel('')
        ax.set_xticks([])
        ax.set_xticklabels([])

def detect_chart_type(ax):
    try:
        lines = ax.get_lines()
        if lines:
            x_data, y_data = lines[0].get_xdata(), lines[0].get_ydata()
        else:
            return 'single_numeric'
    except Exception:
        return 'single_numeric'

    if hasattr(x_data, 'dtype') and np.issubdtype(x_data.dtype, np.datetime64):
        return 'timeseries'
    elif len(x_data) > 0 and isinstance(x_data[0], (float, int)):
        return 'scatter'

    return 'single_numeric'

