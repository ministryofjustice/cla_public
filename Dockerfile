ARG NODE_BASE_IMAGE="node:10"
ARG ALPINE_BASE_IMAGE="alpine:3.15"
ARG BASE_REQUIREMENTS_FILE="requirements.txt"

FROM ${NODE_BASE_IMAGE} as node_build
COPY ./package.json ./package-lock.json ./
RUN npm install
COPY ./cla_public/static-src ./cla_public/static-src
COPY ./gulpfile.js .
COPY ./tasks ./tasks
RUN ./node_modules/.bin/gulp build

FROM ${ALPINE_BASE_IMAGE}
ARG BASE_REQUIREMENTS_FILE

COPY --from=node_build ./cla_public/static/ /home/app/flask/cla_public/static/

RUN apk add --no-cache \
      pcre \
      curl \
      bash \
      gettext \
      nginx\
      python2-dev\
      tzdata && \
    adduser -D www-data -G www-data

RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
RUN python get-pip.py

# To install python dependencies
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


ENV APP_HOME /home/app/flask
WORKDIR /home/app/flask

COPY requirements.txt .
COPY requirements/ requirements/
RUN pip install -r ${BASE_REQUIREMENTS_FILE} &&  pip install -r requirements/generated/requirements-no-deps.txt --no-deps

COPY ./docker/nginx.conf /etc/nginx/nginx.conf

RUN mkdir /var/run/supervisor/
RUN chown -R www-data: /var/run/
RUN chown -R www-data: /var/log/
RUN chown -R www-data /var/lib/nginx/

COPY . .

# Compile translations
RUN pybabel compile -f -d cla_public/translations

USER 1000
EXPOSE 8000

CMD ["supervisord", "--configuration=/home/app/flask/docker/supervisord.conf"]
