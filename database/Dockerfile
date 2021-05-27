FROM python:3.8-slim

ENV CONTAINER_HOME=/usr/src/app/

RUN mkdir -p ${CONTAINER_HOME}

ADD . $CONTAINER_HOME
WORKDIR $CONTAINER_HOME

RUN pip install -r requirements.txt

EXPOSE 80