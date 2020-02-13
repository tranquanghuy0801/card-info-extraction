# FROM ubuntu:18.04 

# MAINTAINER Huy Tran "huy.tran02@base.vn"

# RUN apt-get update -y \
#     && apt-get install -y \
#     python3-dev \
#     python3-pip \
#     libsm6 \
#     libxext6 \
#     build-essential\
#     pkg-config 

# COPY . /app

# WORKDIR /app

# RUN pip3 install -r requirements.txt

# RUN pip3 install gunicorn

# RUN mkdir log

# RUN touch log/logger.log

# CMD ["gunicorn", "--workers=2", "--worker-class=gthread", "-b 0.0.0.0:5000", "server:app", "--log-level=debug", "--log-file=log/logger.log"]

# EXPOSE 5000

FROM ubuntu:18.04
RUN apt-get update -y \
    && apt install python3 -y \
    && apt install python3-pip -y \
    && apt install python3-venv -y 

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY . /app
WORKDIR /app

RUN pip install flask opencv-python google-cloud-vision unidecode gunicorn

# Run the application:
EXPOSE 5000
CMD ["gunicorn", "--workers=2", "--worker-class=gthread", "-b 0.0.0.0:5000", "server:app"]


# FROM python:3.6
# WORKDIR /app
# COPY . /app
# RUN pip install flask opencv-python google-cloud-vision unidecode gunicorn
# EXPOSE 5000 
# CMD ["gunicorn", "--workers=2", "--worker-class=gthread", "-b 0.0.0.0:5000", "server:app"]


