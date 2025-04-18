# OLAP Analysis
#### Developer: Derek Fintel
#### Contact: s542635@youremail; 555-abc-1234

### Project Intro
This README covers an overiew of a brief OLAP (Online Analytical Processing) project. 

### Preliminary Setup Steps
### 1. The Business Goal
```
For this project we wanted to access specific tables within our 'smart_sales.db' to generate business insights pertinent to supporting potential advertising and product development strategies. 

In particular, we sought to leverage our tools to generate understandings of:
- What are the total sales per day of the week?
- What are the total sales per day of the PER a given region?
- What are the total sales per day of a given product?
```
### 2. Data Source
```
We used two tables from our data warehouse, "Sales" and "Customers".

From previous work we have established a data warehouse ('smart_sales.db') that has been built by intaking raw business data via CSV and performing various Python & SQL scripts that prep, scrub, and publish data. These programs were part of an ETL process that cleaned and transformed our datas, even to their table relationships and columns names. 

For our analysis, we utilized the following columns:
**cube.columns:**
[('DayOfWeek', ''), ('product_id', ''), ('customer_id', ''), ('region', ''), ('sale_amount', 'sum'), ('sale_amount', 'mean'), ('transaction_id', 'count'), ('region', 'count')]
**explicit_columns:**
['DayOfWeek', 'product_id', 'customer_id', 'region', 'sale_amount_sum', 'sale_amount_mean', 'transaction_id_count', 'transaction_id']

len(cube.columns): 8
```
### 3. Tools
```
1. Tell us what tools you used and why.
```
### 4. Workflow & Logic
```
1. Describe the dimensions and aggregations - the logic needed for your analysis
2. If using a graphical tool like Power BI or Tableau Prep, use screenshots to show your work. 
```
### 5. Results
```
1. Present your insights with narrative and visualizations.

2. Explain any suggested actions based on the results you uncovered.
```

### 6. Suggested Business Action
```
1. What actions are recommended based on your work

```

### 7. Challenges
```
1. Mention any challenges you encountered and how they were resolved.
```