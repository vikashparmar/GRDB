FROM python:3.9-slim-buster

COPY . /opt/app

WORKDIR /opt/app

RUN pip install -r requirements.txt

ENTRYPOINT ["/usr/local/bin/python3.9", "sqs_listener.py"]