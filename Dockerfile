FROM alpine:3.15

RUN apk add --no-cache \
      pcre \
      curl \
      bash \
      gettext \
      nginx\
      python2-dev\
      npm \
      py2-pip \
      supervisor \
      tzdata \
      uwsgi-python && \
    adduser -D www-data -G www-data

RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
RUN python get-pip.py

# To install python and nodejs dependencies
RUN apk add --no-cache \
      autoconf \
      automake \
      build-base \
      git \
      libffi-dev \
      nasm \
      openssl-dev \
      zlib-dev


RUN cp /usr/share/zoneinfo/Europe/London /etc/localtime
RUN pip install -U setuptools pip==18.1 wheel

ENV APP_HOME /home/app/flask
WORKDIR /home/app/flask

COPY requirements.txt .
COPY requirements/ requirements/
RUN pip install -r requirements.txt &&  pip install -r requirements/generated/requirements-no-deps.txt --no-deps

COPY package.json package-lock.json ./
RUN npm install

COPY ./docker/nginx.conf /etc/nginx/nginx.conf

RUN mkdir /var/run/supervisor/
RUN chown -R www-data: /var/run/
RUN chown -R www-data: /var/log/
RUN chown -R www-data /var/tmp/nginx
RUN chown -R www-data /var/lib/nginx/

COPY . .

# Compile frontend assets and translations
RUN ./node_modules/.bin/gulp build && \
    pybabel compile -f -d cla_public/translations

USER 1000
EXPOSE 8000

CMD ["supervisord", "--configuration=/home/app/flask/docker/supervisord.conf"]
