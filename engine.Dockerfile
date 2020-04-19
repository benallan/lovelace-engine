FROM python:3.7-slim
LABEL maintainer="project.ada.lovelace@gmail.com"

ENV PYTHONIOENCODING=utf-8
ENV LANG='C.UTF-8' LANGUAGE='en_US:en' LC_ALL='C.UTF-8'
ENV ENGINE_PORT=14714

WORKDIR /app

COPY ./requirements_engine.txt /app/requirements_engine.txt
COPY ./requirements_code_runner.txt /app/requirements_code_runner.txt
COPY ./code_runner.Dockerfile /app/code_runner.Dockerfile
# COPY ../lovelace-problems/problems /app/problems
# COPY ../lovelace-problems/problems/resources /app/problems/resources
# COPY ../lovelace-solutions/solutions /app/solutions

# VOLUME $PWD/engine /app/engine
# VOLUME /Users/ben/projects/project-lovelace/lovelace-engine/engine /app/engine

EXPOSE $ENGINE_PORT

RUN apt-get update &&\
  apt-get install -y --no-install-recommends docker.io &&\
  pip install -r requirements_engine.txt &&\
  rm requirements_engine.txt

# CMD ["gunicorn", "--workers", "1", "--log-level", "debug", "--timeout", "600", "--preload", "--reload", "--bind", "localhost:${ENGINE_PORT}", "engine.api:app"]
# CMD gunicorn --workers 1 --log-level debug --timeout 600 --preload --reload --bind localhost:${ENGINE_PORT} engine.api:app
CMD gunicorn --workers 1 --log-level debug --timeout 600 --preload --reload --bind 0.0.0.0:${ENGINE_PORT} engine.api:app
# CMD gunicorn --workers 1 --log-level debug --timeout 600 --preload --reload --bind 0.0.0.0:14714 engine.api:app
#CMD /bin/bash

