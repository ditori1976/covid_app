FROM jenkins/jenkins:ltsd
USER root
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app
RUN pwd


