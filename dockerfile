# syntax=docker/dockerfile:1

# pull official base image
FROM python:3.7.9

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update
COPY requirements.txt /usr/src/app
RUN pip3 install -r requirements.txt
# copy project
COPY main.py /usr/src/app/
COPY start.sh /usr/src/app/

EXPOSE 8001

RUN chmod +x ./start.sh
CMD ["./start.sh"]