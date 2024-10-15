FROM python:latest

RUN pip install kubernetes

WORKDIR /app

COPY controller/ controller/
RUN mkdir logs

ENTRYPOINT ["python", "controller/controller.py"]