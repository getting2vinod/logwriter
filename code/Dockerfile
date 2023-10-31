FROM python:3.9
RUN mkdir -p /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN cd /app && pip install -r requirements.txt