FROM python:3.13.13-alpine3.23 AS compile-image

WORKDIR /app
COPY requirements.txt /app/requirements.txt
ENV PATH="/app/venv/bin:$PATH"
RUN python -m venv /app/venv \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

FROM python:3.13.13-alpine3.23 AS build-image
COPY --from=compile-image /app/venv /app/venv

RUN apk update && apk upgrade
RUN apk --no-cache add \
    git \
    openjdk17-jre

ARG ALLURE_VERSION=2.39.0
RUN wget -q -O /tmp/allure-commandline.tgz "https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.tgz" \
    && tar -zxf /tmp/allure-commandline.tgz -C / \
    && rm /tmp/allure-commandline.tgz
ENV PATH="/allure-${ALLURE_VERSION}/bin:${PATH}"

ENV PATH="/app/venv/bin:$PATH"
WORKDIR /app
