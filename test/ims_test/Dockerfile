FROM ubuntu:23.04

RUN apt-get update -y
RUN apt-get upgrade -y
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get install python3-pip -y
RUN apt-get install curl -y

# Nano for debugging purposes
RUN apt-get install nano

# Flask version needs to be >=2.2 for --app option, Ubuntu >=23.04 is needed for this

RUN apt install python3-flask -y
RUN apt install python3-kubernetes -y

# apt packaged pydantic version is very old
RUN pip install pydantic --break-system-packages

EXPOSE 5000

RUN mkdir -p /app/db

WORKDIR /app

COPY flaskserver.py scripts/flaskserver.py
COPY IMSBackend/ scripts/IMSBackend/

ENTRYPOINT ["flask", "--app", "scripts/flaskserver.py", "run", "--host=0.0.0.0"]