FROM python:3.7-slim
LABEL maintainer="project.ada.lovelace@gmail.com"

WORKDIR /root

COPY ./requirements_code_runner.txt /root/requirements_code_runner.txt

# TODO: copy in permanent code run stuff?

ENV PYTHONIOENCODING=utf-8
ENV LANG='C.UTF-8' LANGUAGE='en_US:en' LC_ALL='C.UTF-8'

# TODO: use REQUIRE file for julia?

RUN apt-get update &&\
  apt-get install -y curl &&\
  apt-get install -y build-essential &&\
  apt-get install -y nodejs &&\
  apt-get install -y julia &&\
  julia -e 'import Pkg; Pkg.add("JSON");' &&\
  pip install -r requirements_code_runner.txt &&\
  rm requirements_code_runner.txt

CMD ["tail", "-f", "/dev/null"]
