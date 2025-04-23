import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pathlib
import sys

# For local imports
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from utils.logger import logger  # noqa: E402

# Constants
OLAP_OUTPUT_DIR: pathlib.Path = pathlib.Path("data").joinpath("olap_cubing_outputs")
CUBED_FILE: pathlib.Path = OLAP_OUTPUT_DIR.joinpath("multidimensional_olap_cube.csv")
RESULTS_OUTPUT_DIR: pathlib.Path = pathlib.Path("data").joinpath("results")
RESULTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_olap_cube(file_path: pathlib.Path) -> pd.DataFrame:
    try:
        cube_df = pd.read_csv(file_path)
        logger.info(f"OLAP cube data successfully loaded from {file_path}.")
        return cube_df
    except Exception as e:
        logger.error(f"Error loading OLAP cube data: {e}")
        raise


def analyze_sales_by_weekday(cube_df: pd.DataFrame) -> pd.DataFrame:
    try:
        sales_by_weekday = (
            cube_df.groupby("DayOfWeek")["sale_amount_sum"].sum().reset_index()
        )
        sales_by_weekday.rename(columns={"sale_amount_sum": "TotalSales"}, inplace=True)
        sales_by_weekday.sort_values(by="TotalSales", inplace=True)
        logger.info("Sales aggregated by DayOfWeek successfully.")
        return sales_by_weekday
    except Exception as e:
        logger.error(f"Error analyzing sales by DayOfWeek: {e}")
        raise


# Analyze sales by DayOfWeek and Region
def analyze_sales_by_day_and_region(cube_df: pd.DataFrame) -> pd.DataFrame:
    try:
        region_day_sales = (
            cube_df.groupby(["DayOfWeek", "region"])["sale_amount_sum"]
            .sum()
            .reset_index()
        )
        logger.info("Sales aggregated by DayOfWeek and Region successfully.")
        return region_day_sales
    except Exception as e:
        logger.error(f"Error analyzing sales by region and weekday: {e}")
        raise

def analyze_sales_by_category_and_region(cube_df: pd.DataFrame, category: str) -> pd.DataFrame:
    try:
        filtered_df = cube_df[cube_df["category"] == category]
        sales_by_category_region = (
            filtered_df.groupby("region")["sale_amount_sum"]
            .sum()
            .reset_index()
            .rename(columns={"sale_amount_sum": "TotalSales"})
        )
        logger.info(f"Sales by region for category '{category}' successfully aggregated.")
        return sales_by_category_region
    except Exception as e:
        logger.error(f"Error analyzing sales by category and region: {e}")
        raise

def analyze_sales_by_region_and_month(cube_df: pd.DataFrame) -> pd.DataFrame:
    try:
        # Ensure that the 'date' or 'order_date' column is in datetime format
        cube_df['sale_date'] = pd.to_datetime(cube_df['sale_date'])

        # Extract month and year from the 'date' column
        cube_df['month'] = cube_df['sale_date'].dt.to_period('M')

        # Grouping by region and month, summing up the sales
        sales_by_region_month = (
            cube_df.groupby(["region", "month"])["sale_amount_sum"]
            .sum()
            .reset_index()
            .rename(columns={"sale_amount_sum": "TotalSales"})
        )

        logger.info("Sales by region and month successfully aggregated.")
        return sales_by_region_month
    except Exception as e:
        logger.error(f"Error analyzing sales by region and month: {e}")
        raise

def analyze_category_sales_by_region_and_month(cube_df: pd.DataFrame, category: str) -> pd.DataFrame:
    try:
        cube_df['sale_date'] = pd.to_datetime(cube_df['sale_date'])
        cube_df['month'] = cube_df['sale_date'].dt.to_period('M')
        filtered_df = cube_df[cube_df['category'] == category]

        category_region_month_sales = (
            filtered_df.groupby(['region', 'month'])['sale_amount_sum']
            .sum()
            .reset_index()
            .rename(columns={'sale_amount_sum': 'TotalSales'})
        )

        logger.info(f"Monthly sales for category '{category}' by region successfully aggregated.")
        return category_region_month_sales
    except Exception as e:
        logger.error(f"Error analyzing category sales by region and month: {e}")
        raise


def analyze_sales_by_category_and_month(cube_df: pd.DataFrame) -> pd.DataFrame:
    try:
        cube_df['sale_date'] = pd.to_datetime(cube_df['sale_date'])
        cube_df['month'] = cube_df['sale_date'].dt.to_period('M')

        sales_by_category_month = (
            cube_df.groupby(['category', 'month'])['sale_amount_sum']
            .sum()
            .reset_index()
            .rename(columns={'sale_amount_sum': 'TotalSales'})
        )

        logger.info("Sales by category and month successfully aggregated.")
        return sales_by_category_month
    except Exception as e:
        logger.error(f"Error analyzing sales by category and month: {e}")
        raise


def identify_least_profitable_day(sales_by_weekday: pd.DataFrame) -> str:
    try:
        least_profitable_day = sales_by_weekday.iloc[0]
        logger.info(
            f"Least profitable day: {least_profitable_day['DayOfWeek']} with revenue ${least_profitable_day['TotalSales']:.2f}."
        )
        return least_profitable_day["DayOfWeek"]
    except Exception as e:
        logger.error(f"Error identifying least profitable day: {e}")
        raise

def visualize_category_sales_by_region(sales_by_category_region: pd.DataFrame, category: str) -> None:
    try:
        plt.figure(figsize=(10, 6))
        sns.barplot(
            x="region",
            y="TotalSales",
            data=sales_by_category_region,
            palette="Set2"
        )
        plt.title(f"Total Sales by Region for Category: {category}", fontsize=16)
        plt.xlabel("Region", fontsize=12)
        plt.ylabel("Total Sales (USD)", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()

        output_path = RESULTS_OUTPUT_DIR.joinpath(f"sales_by_region_for_category_{category}.png")
        plt.savefig(output_path)
        logger.info(f"Category-by-region chart saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing category sales by region: {e}")
        raise

def visualize_sales_by_region_and_month(sales_by_region_month: pd.DataFrame) -> None:
    try:
        plt.figure(figsize=(12, 7))

        # Pivot the dataframe to get regions as columns and months as index
        pivot_df = sales_by_region_month.pivot(index="month", columns="region", values="TotalSales")
        
        # Plotting each region's sales over months
        pivot_df.plot(kind="line", marker='o', figsize=(12, 7), colormap="tab20")
        
        plt.title("Sales by Region Over Months", fontsize=16)
        plt.xlabel("Month", fontsize=12)
        plt.ylabel("Total Sales (USD)", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save and display the plot
        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_by_region_over_months.png")
        plt.savefig(output_path)
        logger.info(f"Sales by region over months chart saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing sales by region over months: {e}")
        raise


def visualize_sales_by_weekday(sales_by_weekday: pd.DataFrame) -> None:
    try:
        plt.figure(figsize=(10, 6))

        # Bar plot for sales
        plt.bar(
            sales_by_weekday["DayOfWeek"],
            sales_by_weekday["TotalSales"],
            color="skyblue",
        )

        # Adding a trendline using Seaborn's regplot
        sns.regplot(
            x=sales_by_weekday.index,  # Using the index as the x-axis for regplot
            y="TotalSales",
            data=sales_by_weekday,
            scatter=False,  # Do not plot the scatter points
            color="red",  # Trendline color
            line_kws={"color": "red", "lw": 2, "ls": "--"}  # Customizing the trendline style
        )

        # Customize the plot
        plt.title("Total Sales by Day of the Week with Trendline", fontsize=16)
        plt.xlabel("Day of the Week", fontsize=12)
        plt.ylabel("Total Sales (USD)", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save and show the plot
        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_by_day_of_week_with_trendline.png")
        plt.savefig(output_path)
        logger.info(f"Visualization with trendline saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing sales by day of the week with trendline: {e}")
        raise

def visualize_category_sales_by_region_and_month(category_region_month_sales: pd.DataFrame, category: str) -> None:
    try:
        pivot_df = category_region_month_sales.pivot(index="month", columns="region", values="TotalSales")
        pivot_df = pivot_df.fillna(0)

        pivot_df.plot(kind="line", marker='o', figsize=(12, 7), colormap="tab20")
        plt.title(f"Monthly Sales Trend by Region for Category: {category}", fontsize=16)
        plt.xlabel("Month")
        plt.ylabel("Total Sales (USD)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        output_path = RESULTS_OUTPUT_DIR.joinpath(f"category_sales_by_region_monthly_{category}.png")
        plt.savefig(output_path)
        logger.info(f"Category sales trend chart by region and month saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing category sales trend by region and month: {e}")
        raise


def visualize_sales_by_category_and_month(sales_by_category_month: pd.DataFrame) -> None:
    try:
        plt.figure(figsize=(12, 7))

        # Convert month back to string for better x-axis spacing
        sales_by_category_month['month'] = sales_by_category_month['month'].astype(str)

        sns.scatterplot(
            data=sales_by_category_month,
            x="month",
            y="TotalSales",
            hue="category",
            palette="tab10",
            s=100,  # dot size
            alpha=0.7
        )

        plt.title("Sales by Category Over Months", fontsize=16)
        plt.xlabel("Month", fontsize=12)
        plt.ylabel("Total Sales (USD)", fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title="Category", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_by_category_over_months_scatter.png")
        plt.savefig(output_path)
        logger.info(f"Category-over-months scatterplot saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing sales by category and month: {e}")
        raise

# Visualize region sales stacked by weekday
def visualize_sales_by_day_and_region(region_day_sales: pd.DataFrame) -> None:
    try:
        pivot_df = region_day_sales.pivot(index="DayOfWeek", columns="region", values="sale_amount_sum")
        pivot_df = pivot_df.fillna(0)

        pivot_df.plot(kind="bar", stacked=True, figsize=(12, 7), colormap="tab20")
        plt.title("Total Sales by Day and Region (Stacked)", fontsize=16)
        plt.xlabel("Day of the Week")
        plt.ylabel("Total Sales (USD)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_by_day_and_region_stacked.png")
        plt.savefig(output_path)
        logger.info(f"Stacked region-by-day chart saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing stacked sales by region: {e}")
        raise


# Heatmap for Region vs DayOfWeek
def visualize_region_heatmap(region_day_sales: pd.DataFrame) -> None:
    try:
        heatmap_data = region_day_sales.pivot(index="region", columns="DayOfWeek", values="sale_amount_sum")
        heatmap_data = heatmap_data.fillna(0)

        plt.figure(figsize=(12, 7))
        sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="Blues")
        plt.title("Sales Heatmap by Region and Day of the Week")
        plt.xlabel("Day of the Week")
        plt.ylabel("Region")
        plt.tight_layout()

        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_heatmap_by_region_and_day.png")
        plt.savefig(output_path)
        logger.info(f"Heatmap saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        raise

#Test1
def visualize_all_categories_sales_by_region_and_month(cube_df: pd.DataFrame) -> None:
    try:
        df = cube_df.copy()
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df['month'] = df['sale_date'].dt.to_period('M').astype(str)

        grouped = (
            df.groupby(['category', 'region', 'month'])['sale_amount_sum']
            .sum()
            .reset_index()
            .rename(columns={'sale_amount_sum': 'TotalSales'})
        )

        # Create FacetGrid
        g = sns.FacetGrid(grouped, col="category", col_wrap=3, height=4, sharey=False)
        g.map_dataframe(sns.lineplot, x="month", y="TotalSales", hue="region", marker='o')
        g.add_legend()
        g.set_titles(col_template="{col_name}")
        g.set_axis_labels("Month", "Total Sales (USD)")
        for ax in g.axes.flatten():
            for label in ax.get_xticklabels():
                label.set_rotation(45)
        plt.tight_layout()

        output_path = RESULTS_OUTPUT_DIR.joinpath("category_sales_by_region_month_facet.png")
        plt.savefig(output_path)
        logger.info(f"Faceted category-region-month sales chart saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing faceted category sales: {e}")
        raise

#Test2
def visualize_category_sales_stacked_area(category_region_month_sales: pd.DataFrame, category: str) -> None:
    try:
        pivot_df = category_region_month_sales.pivot(index="month", columns="region", values="TotalSales")
        pivot_df = pivot_df.fillna(0).astype(float)
        pivot_df.index = pivot_df.index.astype(str)

        pivot_df.plot.area(figsize=(12, 7), colormap='tab20', alpha=0.85)
        plt.title(f"Stacked Area Chart: Monthly Sales by Region for Category '{category}'", fontsize=16)
        plt.xlabel("Month")
        plt.ylabel("Total Sales (USD)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        output_path = RESULTS_OUTPUT_DIR.joinpath(f"category_sales_stacked_area_{category}.png")
        plt.savefig(output_path)
        logger.info(f"Stacked area chart saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing stacked area chart: {e}")
        raise


#Test3
def visualize_category_region_month_heatmap(cube_df: pd.DataFrame, category: str) -> None:
    try:
        df = cube_df[cube_df["category"] == category].copy()
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df['month'] = df['sale_date'].dt.to_period('M').astype(str)

        heat_df = (
            df.groupby(['region', 'month'])['sale_amount_sum']
            .sum()
            .reset_index()
            .pivot(index='region', columns='month', values='sale_amount_sum')
            .fillna(0)
        )

        plt.figure(figsize=(12, 7))
        sns.heatmap(heat_df, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5)
        plt.title(f"Heatmap of Monthly Sales by Region for Category: {category}", fontsize=16)
        plt.xlabel("Month")
        plt.ylabel("Region")
        plt.tight_layout()

        output_path = RESULTS_OUTPUT_DIR.joinpath(f"category_region_month_heatmap_{category}.png")
        plt.savefig(output_path)
        logger.info(f"Heatmap saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error generating heatmap for category '{category}': {e}")
        raise

#Test4
def visualize_category_sales_by_region_and_month_all(cube_df: pd.DataFrame) -> None:
    try:
        df = cube_df.copy()
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df['month'] = df['sale_date'].dt.to_period('M').astype(str)

        grouped = (
            df.groupby(['category', 'region', 'month'])['sale_amount_sum']
            .sum()
            .reset_index()
            .rename(columns={'sale_amount_sum': 'TotalSales'})
        )

        plt.figure(figsize=(12, 7))
        sns.lineplot(
            data=grouped,
            x="month",
            y="TotalSales",
            hue="category",
            style="region",
            markers=True
        )

        plt.title("Monthly Sales Trends by Category and Region", fontsize=16)
        plt.xlabel("Month")
        plt.ylabel("Total Sales (USD)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        output_path = RESULTS_OUTPUT_DIR.joinpath("category_region_month_multiline.png")
        plt.savefig(output_path)
        logger.info("Multi-category region-month line chart saved.")
        plt.show()
    except Exception as e:
        logger.error("Error visualizing multi-category region sales trends: {e}")
        raise

def main():
    try:
        # Load OLAP cube
        cube_df = load_olap_cube(CUBED_FILE)

        # --- Analysis ---
        weekday_sales = analyze_sales_by_weekday(cube_df)
        region_day_sales = analyze_sales_by_day_and_region(cube_df)
        region_month_sales = analyze_sales_by_region_and_month(cube_df)
        category_month_sales = analyze_sales_by_category_and_month(cube_df)

        # Determine the least profitable day
        least_day = identify_least_profitable_day(weekday_sales)
        logger.info(f"Least profitable weekday identified: {least_day}")

        # --- Visualizations ---
        visualize_sales_by_weekday(weekday_sales)
        visualize_sales_by_day_and_region(region_day_sales)
        visualize_region_heatmap(region_day_sales)
        visualize_sales_by_region_and_month(region_month_sales)
        visualize_sales_by_category_and_month(category_month_sales)
        visualize_all_categories_sales_by_region_and_month(cube_df)

        # Get all unique categories
        categories = cube_df['category'].dropna().unique()

        # Run category-specific visualizations
        for category in categories:
            logger.info(f"Generating visualizations for category: {category}")
            cat_region_sales = analyze_sales_by_category_and_region(cube_df, category)
            cat_region_month_sales = analyze_category_sales_by_region_and_month(cube_df, category)

            visualize_category_sales_by_region(cat_region_sales, category)
            visualize_category_sales_by_region_and_month(cat_region_month_sales, category)
            visualize_category_sales_stacked_area(cat_region_month_sales, category)
            visualize_category_region_month_heatmap(cube_df, category)

        logger.info("All analyses and visualizations completed successfully.")

    except Exception as e:
        logger.error(f"Main execution failed: {e}")


if __name__ == "__main__":
    main()