from .decorator import wb_plot
import numpy as np 

@wb_plot(
    title="Employment Trends in East Asia",
    subtitle="2000–2024, percent change",
    note=[
        ("Note:", "Includes data from China, Indonesia, Vietnam."),
        ("Source:", "World Bank LFS Database (2024).")
    ]
)
def plot_employment(axs):
    ax = axs[0]
    ax.plot([2000, 2010, 2020], [55, 65, 72])
    ax.set_ylabel("Employment (%)")

plot_employment()

@wb_plot(
    width=800,
    height=500,
    dpi=100,
    save_path=None,
    title="Government Investment in Key Sectors",
    subtitle="Spending from 2018 to 2024 (adjusted for inflation)",
    note=[("Source:", "National Treasury Budget Papers"),
          ("Note:", "Data adjusted to 2024 dollars using CPI")]
)
def plot_multi_series(axs, *args, **kwargs):
    ax = axs[0]

    x = np.arange(2018, 2025)
    y1 = [10, 15, 20, 23, 25, 27, 30]
    y2 = [5, 8, 12, 16, 20, 21, 24]
    y3 = [2, 4, 8, 10, 15, 18, 20]

    ax.plot(x, y1, label='Education')
    ax.plot(x, y2, label='Healthcare')
    ax.plot(x, y3, label='Transport') 

    # Axis label on Y axis only (WB style for time series)
    ax.set_ylabel("Funding (AU$ millions)")

# Call the decorated function with layout text
plot_multi_series()

# scatterplot
@wb_plot(
    title="GDP vs Life Expectancy",
    subtitle="Scatterplot of synthetic data",
    note=[("Source:", "World Bank (fictional).")]
)
def scatter_plot(axs):
    np.random.seed(0)
    x = np.random.normal(50000, 15000, 100)
    y = np.random.normal(75, 10, 100)

    axs[0].scatter(x, y, label="Countries")
    axs[0].set_xlabel("GDP per capita (USD)")
    axs[0].set_ylabel("Life expectancy (years)")

scatter_plot()

@wb_plot(
    title="Employment by Sector",
    subtitle="Distribution across sectors in 2024",
    note=[("Source:", "World Bank, 2024 dataset.")]
)
def bar_plot(axs):
    sectors = ["Agriculture", "Industry", "Services"]
    values = [22, 30, 48]

    ax = axs[0]
    bars = ax.bar(sectors, values, label="Share of employment")

    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("Sector")

bar_plot()