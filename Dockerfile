# FROM ubuntu:18.04
# RUN apt-get update && apt-get install \
#   -y --no-install-recommends locales python3 python3-virtualenv libgtk2.0-dev

# ENV VIRTUAL_ENV=/opt/venv
# RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# # Install dependencies:
# COPY . .
# RUN pip install -r requirements.txt

# # Run the application:
# EXPOSE 5000
# CMD ["python3", "app/app.py"]

FROM python:3.6
# RUN pip install virtualenv 
# RUN virtualenv -p python3 venv 
# ENV PATH="venv/bin:$PATH"
WORKDIR /app
COPY . /app
RUN pip install flask opencv-python google-cloud-vision unidecode
EXPOSE 5000 
ENTRYPOINT [ "python3","app/app.py"]
