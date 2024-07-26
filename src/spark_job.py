import os
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
from config.config import settings


class SparkJob:
    """
    In order to interact with Amazon AWS S3 from Spark, we need to use the third party library.
    And this library has 3 different options
    1. s3: s3:\\ or s3:// (deprecated)
    2. s3n: s3n:\\ or s3n:// .This is also not the recommended option
    3. s3a: s3a:\\ or s3a:// .This is a replacement of s3n which supports larger files and improves in performance
    """

    def __init__(self):

        self.config = pyspark.SparkConf().setAppName('MySparkApp').setAll([
            ('spark.databricks.service.server.enabled', 'false'),
            ('spark.driver.memory', '5g'),
            ('spark.driver.cores', '2'),
            ('spark.driver.maxResultSize', '1g'),
            ('spark.executor.instances', '4'),
            ('spark.executor.memory', '3g'),
            ('spark.executor.cores', '4'),
            ("spark.sql.join.preferSortMergeJoin", True),
            ("spark.sql.shuffle.partitions", '80'),
            # ("spark.default.parallelism", '80'),
            ("spark.sql.execution.arrow.pyspark.enabled", "true"),
            ("spark.sql.execution.arrow.maxRecordsPerBatch", "10000"),
            ("spark.executor.memoryOverheadFactor", "0.5"),
            ("spark.driver.memoryOverheadFactor", "0.5"),
            ("spark.memory.storageFraction", "0.3"),
            ("spark.jars", f"{os.path.join(settings.BASE_DIR, 'jars', 'spark-sql-kafka-0-10_2.12-3.5.1.jar')},"
                           f"{os.path.join(settings.BASE_DIR, 'jars', 'kafka-clients-3.7.1.jar')},"
                           f"{os.path.join(settings.BASE_DIR, 'jars', 'commons-pool2-2.12.0.jar')},"
                           f"{os.path.join(settings.BASE_DIR, 'jars', 'spark-token-provider-kafka-0-10_2.12-3.5.1.jar')},"
             )
        ])

        self.spark = (
            SparkSession
            .builder
            .master("local[*]")
            .config(conf=self.config)
            .getOrCreate()
            )
        self.spark_context = self.spark.sparkContext

    def read_kafka_stream(self):
        kafka_df = (
            self.spark
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "localhost:9092")
            .option("subscribe", "sqlite-users")
            .option("startingOffsets", "earliest")
            .option("failOnDataLoss", "false")
            .load()
        )
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("full_name", StringType(), True),
            StructField("gender", IntegerType(), True),
            StructField("street", StringType(), True),
            StructField("state", StringType(), True),
            StructField("country", StringType(), True),
            StructField("timezone", StringType(), True),
            StructField("email", StringType(), True),
            StructField("dob", StringType(), True),
            StructField("age", IntegerType(), True),
            StructField("phone", StringType(), True),
            StructField("cell", StringType(), True)
        ])
        kafka_df = kafka_df.selectExpr("CAST(value AS STRING) as json_value")
        processed_df = (
            kafka_df
            .select(F.from_json(F.col("json_value"), StructType([
                StructField("payload", schema, True)
            ])).alias("parsed_value"))
            .select("parsed_value.payload.*")
        )
        # Print to console to check the data
        # query = processed_df.writeStream.format("console").trigger(processingTime="10 seconds").start()

        # Save to csv file
        query = (
            processed_df
            .writeStream
            .format("csv")
            .option("path", os.path.join(settings.BASE_DIR, "output"))
            .option("checkpointLocation", os.path.join(settings.BASE_DIR, "checkpoint"))
            .outputMode("append")
            .start()
        )

        query.awaitTermination()


if __name__ == '__main__':
    spark_job = SparkJob()
    spark_job.read_kafka_stream()
