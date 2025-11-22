FROM 959708567929.dkr.ecr.eu-central-1.amazonaws.com/env/python312:latest as python-base

ARG GEMFURY_TOKEN="F2HmD-QOH98JflhGCHn8CX0A1OgHHPCM"
ARG BUILD_ARG="dev"
ENV VERSION=$BUILD_ARG

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /app
COPY poetry.lock pyproject.toml Makefile /app/

RUN make install mode=stand

COPY . /app

RUN chmod +x ./main.py ./migration.py


CMD ["python", "main.py"]
