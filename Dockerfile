FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV WAIT_VERSION 2.7.2
ENV C_FORCE_ROOT=1

WORKDIR /usr/src/code
COPY requirements.txt /usr/src/code

RUN python -m pip install -r requirements.txt --timeout 500

COPY . /usr/src/code

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait