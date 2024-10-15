FROM python:latest

RUN pip install kubernetes

WORKDIR /app

COPY controller/ controller/

ENTRYPOINT ["python", "controller/controller.py"]