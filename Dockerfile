# pull official base image
FROM python:3.9-alpine

# set work directory
WORKDIR /home/codeinside

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY ENV['SECRET_KEY']
ENV PATH="/home/codeinside/.local/bin:${PATH}"

# install packages
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && apk del build-deps \
    && apk add libc-dev \
    && apk add linux-headers \
    && apk add g++ \
    && apk add openjdk17 --repository http://dl-cdn.alpinelinux.org/alpine/edge/community \
    && apk add npm \
    && apk add mono --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \ 
    && apk add bash \
    && apk add nano

# create user
RUN adduser -D codeinside
USER codeinside

# install dependencies
COPY --chown=codeinside:codeinside ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY --chown=codeinside:codeinside . .

# collect static files
RUN python manage.py collectstatic --noinput

# make migrations
RUN python manage.py makemigrations
RUN python manage.py migrate
