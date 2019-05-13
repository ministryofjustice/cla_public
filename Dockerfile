FROM alpine:3.9

RUN apk add --no-cache \
      bash \
      gettext \
      nginx \
      npm \
      py2-pip \
      supervisor \
      tzdata \
      uwsgi-python && \
    adduser -D www-data -G www-data

# To install python and nodejs dependencies
RUN apk add --no-cache \
      autoconf \
      automake \
      build-base \
      git \
      libffi-dev \
      nasm \
      openssl-dev \
      python2-dev \
      zlib-dev

RUN cp /usr/share/zoneinfo/Europe/London /etc/localtime
RUN pip install -U setuptools pip==18.1 wheel

ENV APP_HOME /home/app/flask
WORKDIR /home/app/flask

COPY requirements.txt .
COPY requirements/ requirements/
RUN pip install -r requirements.txt

COPY package.json package-lock.json ./
RUN npm install

COPY ./docker/nginx.conf /etc/nginx/nginx.conf
COPY ./docker/supervisord-services.ini /etc/supervisor.d/

COPY . .

# Compile frontend assets and translations
RUN ./node_modules/.bin/gulp build && \
    pybabel compile -f -d cla_public/translations

EXPOSE 80

CMD ["supervisord", "--nodaemon"]
