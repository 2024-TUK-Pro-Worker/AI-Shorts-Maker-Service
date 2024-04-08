FROM python:3.11.8-alpine

WORKDIR /home/app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN apk add git
ARG token
RUN git clone https://$token@github.com/2024-TUK-Pro-Worker/AI-Shorts-Maker-Service.git

RUN apk add --no-cache ffmpeg

COPY .env .env

WORKDIR /home/app/AI-Shorts-Maker-Service

#CMD [ "python3", "main.py"]