FROM ubuntu:23.04

RUN apt-get update -y
RUN apt-get upgrade -y
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get install python3-pip -y

# Nano and Curl for debugging purposes
RUN apt-get install curl -y
RUN apt-get install nano

RUN pip install "fastapi[standard]" --break-system-packages
RUN pip install deepdiff --break-system-packages
RUN apt install python3-kubernetes -y

EXPOSE 5000

WORKDIR /scripts

COPY fastapiserver.py fastapiserver.py
COPY backend/ backend/
COPY utils/ utils/
RUN mkdir logs
RUN chmod +x utils/post_start.sh

ENTRYPOINT ["fastapi", "dev", "fastapiserver.py", "--host=0.0.0.0", "--port=5000"]
