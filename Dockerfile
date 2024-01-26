FROM python:3.11.7-alpine3.18 AS compile-image

WORKDIR /app
COPY requirements.txt /app/requirements.txt
ENV PATH="/app/venv/bin:$PATH"
RUN python -m venv /app/venv
RUN pip3 install --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir -r requirements.txt

FROM python:3.11.7-alpine3.18 AS build-image
COPY --from=compile-image /app/venv /app/venv

RUN apk --no-cache add \
    git \
    openjdk8-jre \
    && rm -rf /var/cache/apk/*

ENV VERSION 2.26.0
RUN wget https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/$VERSION/allure-commandline-$VERSION.tgz
RUN tar -zxf allure-commandline-$VERSION.tgz
RUN rm allure-commandline-${VERSION}.tgz
ENV PATH="/allure-${VERSION}/bin:${PATH}"

ENV PATH="/app/venv/bin:$PATH"
WORKDIR /app
