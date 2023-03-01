FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN apt-get update \
    && apt-get install -y git

COPY . /code/

RUN pip install huggingface-hub
RUN pip install psycopg2-binary
RUN pip install boto3
RUN pip install git+https://github.com/ranjan-stha/reports_generator

CMD [ "python", "./app.py" ]
