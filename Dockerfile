FROM ubuntu:18.04 

MAINTAINER Huy Tran "huy.tran02@base.vn"

RUN apt-get update -y \
    && apt-get install -y \
    python3-dev \
    python3-pip \
    libsm6 \
    libxext6 \
    build-essential\
    pkg-config \
    gunicorn3


COPY app /app

COPY requirements.txt /app/requirements.txt

COPY harrytext-ocr.json /app/harrytext-ocr.json

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN mkdir log

RUN touch log/logger.log

CMD ["gunicorn3", "--workers=1", "--worker-class=gthread", "-b 0.0.0.0:5000", "app:app", "--log-level=debug", "--log-file=log/logger.log"]

EXPOSE 5000


# FROM python:3.6
# WORKDIR /app
# COPY . /app
# RUN pip install flask opencv-python google-cloud-vision unidecode
# EXPOSE 5000 
# ENTRYPOINT [ "python3","app/app.py"]


