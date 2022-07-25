FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk --update add
RUN apk add gcc libc-dev libffi-dev jpeg-dev zlib-dev libjpeg ffmpeg

RUN pip install --upgrade pip
RUN pip install aiogram vk-api beautifulsoup4 streamlink

COPY . .