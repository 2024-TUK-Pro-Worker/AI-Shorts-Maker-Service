# LOCAL
FROM python:3.11.8-alpine as build
# SERVER
#FROM --platform=linux/amd64 python:3.11.8-alpine as build

WORKDIR /home/app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN apk add git
ARG token
RUN git clone https://$token@github.com/2024-TUK-Pro-Worker/AI-Shorts-Maker-Service.git

RUN apk add --no-cache ffmpeg

WORKDIR /home/app/AI-Shorts-Maker-Service

COPY .env .env

CMD [ "python3", "main.py"]