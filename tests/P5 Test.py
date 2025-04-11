# Verify Spark works
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("SmartSales").getOrCreate()
print(spark)