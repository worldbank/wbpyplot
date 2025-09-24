# wbpyplot

The World Bank `matplotlib` theme.

## Installation

Install the package with `pip install git+https://github.com/worldbank/wbpyplot`.

## Using the package

When the package is installed, load the function decorator into your Python session like so:

```
from wbpyplot import wb_plot
```


### wb_plot

`wb_plot` is the mai function decorator which styles all `matplotlib` (and derivatives, such as `seaborn`). Add it on top of a function calling `matlotlib` elements.

For example: 

```
@wb_plot(
    width=800,
    height=500,
    dpi=100,
    save_path=None,
    title="Government Investment in Key Sectors",
    subtitle="Spending from 2018 to 2024 (adjusted for inflation)",
    note=[
        ("Source:", "National Treasury Budget Papers"),
        ("Note:", "Data adjusted to 2024 dollars using CPI"),
    ],
)
def plot_multi_series(axs, *args, **kwargs):
    ax = axs[0]

    x = np.arange(2018, 2025)
    y1 = [10, 15, 20, 23, 25, 27, 30]
    y2 = [5, 8, 12, 16, 20, 21, 24]
    y3 = [2, 4, 8, 10, 15, 18, 20]

    ax.plot(x, y1, label="Education")
    ax.plot(x, y2, label="Healthcare")
    ax.plot(x, y3, label="Transport")

    # Axis label on Y axis only (WB style for time series)
    ax.set_ylabel("Funding (AU$ millions)")


# Call the decorated function with layout text
plot_multi_series()
```

The theme

- changes the font of all text to Open Sans.
- styles the title, subtitle, caption, axes and legends according to the [World Bank data visualization style guide](https://wbg-vis-design.vercel.app/).

To apply the World Bank color palettes to your visualizations, see the 'Colors' section below.

On top of that, the theme has some specific style settings for certain chart types.

With time series line graphs, the vertical grid lines, the X axis title and the Y axis title are removed. 

For line charts, the x aesthetic should be mapped to a date variable, and the y aesthetic to a numerical variable.

With bar or column graphs, both vertical and horizontal grid lines are removed, the X axis is moved to the top, and the bar labels are capitalized and bolded. The X axis title is removed, but can be added manually.

For bar charts, the x aesthetic should be mapped to a numerical variable, and the y aesthetic to a discrete variable.

The World Bank data visualization style calls for value labels next to the bars, which are added by default.

```
@wb_plot(
    title="Employment by Sector",
    subtitle="Distribution across sectors in 2024",
    note=[("Source:", "World Bank, 2024 dataset.")],
)
def bar_plot(axs):
    sectors = ["Agriculture", "Industry", "Services"]
    values = [22, 30, 48]

    ax = axs[0]
    bars = ax.bar(sectors, values, label="Share of employment")

    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("Sector")


bar_plot()
```

Note that `wbpyplot`, unlike `wbplot`, does not currently support beeswarm charts. 

With a scatter plot, the plot is only styled, but no chart elements (such as the Y axis grid lines, for example) are removed.

For scatter plots, both the x and the y aesthetic should be mapped to a numerical variable.

```
@wb_plot(
    title="GDP vs Life Expectancy",
    subtitle="Scatterplot of synthetic data",
    note=[("Source:", "World Bank (fictional).")],
)
def scatter_plot(axs):
    np.random.seed(0)
    x = np.random.normal(50000, 15000, 100)
    y = np.random.normal(75, 10, 100)

    axs[0].scatter(x, y, label="Countries")
    axs[0].set_xlabel("GDP per capita (USD)")
    axs[0].set_ylabel("Life expectancy (years)")


scatter_plot()
```


### Colors

#### All colors

All World Bank Data Visualization colors are available through the style guide.

#### Color scales

`wbpyplot` comes with several color scales.

The following palettes are available for mapping discrete variables to chart markers. When the `palette` parameter matches the mapped level variable, the levels will be automatically matched to their corresponding colors. The available discrete palettes and their levels are:

* `wb_categorical`: the default palette, with 9 distinct colors.
* `wb_region`: colors for regions. Matches the levels "WLD", "NAC", "LCN", "SAS", "MEA", "ECS", "EAS", "SSF", "AFE" and "AFW"
* `wb_income`: colors for income classes. Matches the levels "HIC", "UMIC", "LMIC" and "LIC".
* `wb_gender`: colors for gender. Matches the levels "male", "female" and "diverse"
* `wb_urbanisation`: colors for urbanisation. Matches the levels "urban" and "rural".
* `wb_age`: colors for age classes. Matches the levels "youngestAge", "youngerAge", "middleAge", "olderAge" and "oldestAge"
* `wb_binary`: colors for binary variables. Matches the levels "yes" and "no"

Continuous color scales are available for sequential and diverging palettes. 

* `wb_div_default`: This diverging scale works best when showing numbers with a connotation of good/bad for higher or lower values (e.g. GDP growth). Use the warmer shades for the numbers with the more negative connotation and the cooler shades to show positive values.
* `wb_div_alt`: This diverging scale can be used as an alternative for the Default diverging scale if you want to emphasize the negative connotation of the numbers more strongly.
* `wb_div_neutral`: This diverging scale was designed to work well in conditions when showing numbers without a clear connotation of good/bad for higher or lower values (e.g. growth in urban vs rural living).

If you want to sample a small number of colors from the palette, add the parameter `palette_n = 2` to the function decorator - changing the integer for your number of colors. The function will select the first two hex codes in the list from the defined color palette. 

If you have a continous colour scale (i.e. a scale with "seq" or "div" in the name) and want to bin the values into certain categories, set `palette_bins` argument. The answer can be one of the following:

* `None`: no discretization (continuous colormap).
* an int: number of equally spaced bins.
* a sequence: explicit bin edges.
        
Likewise if you want to break the bins into linear or other discrete bin sizes, set `palette_bin_mode` to one of "linear" or "quantile". Only applies when `palette_bins` is specified.

```    
@wb_plot(
    title="Binned with Explicit Thresholds",
    subtitle="Custom edges: [50, 60, 70, 80, 90, 100]",
    note=[("Source:", "World Bank, 2024 dataset.")],
    palette="wb_seq_bad_to_good",
    palette_bins=[50, 60, 70, 80, 90, 100],  # <- explicit edges
)
def heatmap_edges(axs):
    ax = axs[0]
    data = np.random.default_rng(2).integers(50, 96, size=(10, 10))
    im = ax.imshow(data)
    ax.figure.colorbar(im, ax=ax, label="Literacy (%)")

heatmap_edges()
```
