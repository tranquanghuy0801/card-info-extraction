FROM python:3.6 
LABEL maintainer="huy.tran02@base.vn"
RUN mkdir -p /app
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5000 
ENTRYPOINT [ "python3","app/app.py"]