FROM ubuntu:18.04

MAINTAINER Sindre Henriksen "sid.henriksen@gmail.com"

RUN apt-get update
RUN apt-get update -y &&\
    apt-get install -y python3-pip python3-dev curl jq

RUN mkdir app 
COPY /requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod +x /app/src/fetch_data.sh

WORKDIR /app/src

ENTRYPOINT /app/src/fetch_data.sh
