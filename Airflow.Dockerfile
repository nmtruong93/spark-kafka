FROM apache/airflow:2.5.1-python3.8

USER root
RUN apt-get update && apt-get install -y vim

USER airflow
WORKDIR /opt/airflow

COPY ./requirements.txt /opt/airflow/requirements.txt

RUN pip install --default-timeout=86400 future --no-cache-dir -r /opt/airflow/requirements.txt
RUN pip uninstall -y dataclasses

COPY . /opt/airflow

ENV PYTHONPATH "${PYTHONPATH}:/opt/airflow"

EXPOSE 8080