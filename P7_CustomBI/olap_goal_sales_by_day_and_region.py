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


def visualize_sales_by_weekday(sales_by_weekday: pd.DataFrame) -> None:
    try:
        plt.figure(figsize=(10, 6))
        plt.bar(
            sales_by_weekday["DayOfWeek"],
            sales_by_weekday["TotalSales"],
            color="skyblue",
        )
        plt.title("Total Sales by Day of the Week", fontsize=16)
        plt.xlabel("Day of the Week", fontsize=12)
        plt.ylabel("Total Sales (USD)", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()

        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_by_day_of_week.png")
        plt.savefig(output_path)
        logger.info(f"Visualization saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing sales by day of the week: {e}")
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

    logger.info("Full analysis and visualization completed.")


if __name__ == "__main__":
    main()
