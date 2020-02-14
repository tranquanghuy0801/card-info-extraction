FROM python:3.6-slim-stretch

RUN apt-get update -y \
    && apt-get install libgtk2.0-dev -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV VIRTUAL_ENV=/venv PATH="/venv/bin:$PATH"
RUN python -m venv /venv

# Install dependencies:
COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

RUN mkdir log

RUN touch log/logger.log

# Run the application:
EXPOSE 5000
CMD ["gunicorn", "--workers=2", "--worker-class=gthread", "-b 0.0.0.0:5000", "server:app","--log-level=debug", "--log-file=log/logger.log"]


