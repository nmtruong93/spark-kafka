### Install Docker
Install Docker from [here](https://docs.docker.com/desktop/install/mac-install/)

Please note that all the below flows are tested on Mac OS. If you are using Windows, please make sure to update the paths accordingly.

### Start Airflow to run ETL and insert data to SQLite
1. Open a new terminal  and start Airflow
    ```bash
      docker-compose up
    ```
2. Open Airflow UI and see if the DAG is running
    ```bash
      http://localhost:8080
    ```
    Credentials:
    ```bash
      username: airflow
      password: airflow
    ```
3. Check the DAG `WEB-CRAWLER` and see if the tasks are running successfully

4. SQLite volume is mounted to the host machine, so you can see the data in the host machine
    ```bash
      sqlite3 user.db
    ```

### Start kafka and send data from SQLite to Kafka
1. Open a new terminal and start zookeeper
    ```bash
    ./kafka_2.12-3.7.1/bin/zookeeper-server-start.sh ./kafka_2.12-3.7.1/config/zookeeper.properties
    ```
2. Open a new terminal and start kafka
    ```bash
    ./kafka_2.12-3.7.1/bin/kafka-server-start.sh ./kafka_2.12-3.7.1/config/server.properties
    ```

3. Open a new terminal and create topic. This topic must be the same name in the `connect-sqlite-source.properties` file
    ```bash
    ./kafka_2.12-3.7.1/bin/kafka-topics.sh --create --topic sqlite-users --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ```

4. List topics to check if the topic is created
    ```bash
    ./kafka_2.12-3.7.1/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
    ```

5. Describe topic to check the topic details
    ```bash
    ./kafka_2.12-3.7.1/bin/kafka-topics.sh --describe --topic sqlite-users --bootstrap-server localhost:9092
    ```

6. Test produce message to the topic (Optional)
    ```bash
    ./kafka_2.12-3.7.1/bin/kafka-console-producer.sh --topic sqlite-users --bootstrap-server localhost:9092
    ```
    Enter some data
    ```python
    {"id": 1, "full_name": "John Doe", "gender": "male", "country": "USA"}
    {"id": 2, "full_name": "Jane Doe", "gender": "female", "country": "USA"}
    ```

7. Open a new terminal and test consume message from the topic
    ```bash
    ./kafka_2.12-3.7.1/bin/kafka-console-consumer.sh --topic sqlite-users --from-beginning --bootstrap-server localhost:9092
    ```
   
8. Open file `connect-sqlite-source.properties` and update the path of the SQLite database file
   ```python
    connection.url=jdbc:sqlite:path/to/user.db
   ```   

9. Send data from SQLite to Kafka topic users
    ```bash
    ./kafka_2.12-3.7.1/bin/connect-standalone.sh ./kafka_2.12-3.7.1/config/connect-standalone.properties ./connect-sqlite-source.properties
    ```

10. Stop kafka
    ```bash
    ./kafka_2.12-3.7.1/bin/kafka-server-stop.sh
    ```
11. Stop zookeeper
    ```bash
    ./kafka_2.12-3.7.1/bin/zookeeper-server-stop.sh
    ```
12. Delete topic
    ```bash
    ./kafka_2.12-3.7.1/bin/kafka-topics.sh --delete --topic sqlite-users --bootstrap-server localhost:9092
    ```

### Run Spark job to read data from Kafka and write to csv
1. Install spark 3.5.1 in local machine with scala 2.12
2. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
3. Run spark job
    ```python
        python spark_job.py
    ```
4. Check the result in the `output` folder



