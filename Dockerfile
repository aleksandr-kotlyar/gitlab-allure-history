FROM python:3.7.9-alpine3.13 AS compile-image

WORKDIR /app
COPY requirements.txt /app/requirements.txt
ENV PATH="/app/venv/bin:$PATH"
RUN python -m venv /app/venv
RUN pip3 install --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir -r requirements.txt

FROM python:3.7.9-alpine3.13 AS build-image
COPY --from=compile-image /app/venv /app/venv

RUN apk --no-cache add \
    git=2.30.1-r0 \
    curl=7.74.0-r1 \
    openjdk8-jre=8.275.01-r0 \
    && rm -rf /var/cache/apk/*

ENV VERSION 2.13.8
RUN wget https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/$VERSION/allure-commandline-$VERSION.tgz
RUN tar -zxf allure-commandline-$VERSION.tgz
RUN rm allure-commandline-${VERSION}.tgz
ENV PATH="/allure-${VERSION}/bin:${PATH}"

ENV PATH="/app/venv/bin:$PATH"
WORKDIR /app
