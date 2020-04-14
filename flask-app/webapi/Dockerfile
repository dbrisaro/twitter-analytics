FROM ubuntu:18.04

MAINTAINER Den Delimarsky "d@dsc.ai"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3.8 build-essential libpq-dev python3.8-venv socat

COPY . /webapi

WORKDIR /webapi

RUN python3.8 -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN chmod +x boot.sh

EXPOSE 5001
ENTRYPOINT ["./boot.sh"]