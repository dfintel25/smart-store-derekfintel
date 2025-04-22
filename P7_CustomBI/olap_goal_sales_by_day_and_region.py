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


def main():
    logger.info("Starting SALES_LOW_REVENUE_DAYOFWEEK analysis...")

    cube_df = load_olap_cube(CUBED_FILE)

    sales_by_weekday = analyze_sales_by_weekday(cube_df)
    least_profitable_day = identify_least_profitable_day(sales_by_weekday)
    logger.info(f"Least profitable day: {least_profitable_day}")
    visualize_sales_by_weekday(sales_by_weekday)

    # Analysis and visualizations
    region_day_sales = analyze_sales_by_day_and_region(cube_df)
    visualize_sales_by_day_and_region(region_day_sales)
    visualize_region_heatmap(region_day_sales)

    # Analyze sales by region and month
    region_month_sales = analyze_sales_by_region_and_month(cube_df)

    # Visualize sales by region and month
    visualize_sales_by_region_and_month(region_month_sales)

    # Analyze and visualize category-month sales
    category_month_sales = analyze_sales_by_category_and_month(cube_df)
    visualize_sales_by_category_and_month(category_month_sales)

    # Category-Region Sales Analysis
    target_category = "Electronics"  # Change this as needed or make it a CLI arg
    category_region_sales = analyze_sales_by_category_and_region(cube_df, target_category)
    visualize_category_sales_by_region(category_region_sales, target_category)

    # New: Category-Region-Month Trend
    category_region_month_sales = analyze_category_sales_by_region_and_month(cube_df, target_category)
    visualize_category_sales_by_region_and_month(category_region_month_sales, target_category)


    logger.info("Full analysis and visualization completed.")


if __name__ == "__main__":
    main()
