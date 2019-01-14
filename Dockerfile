#
# CLA Dockerfile
#
# https://github.com/dockerfile/nginx
#
# Pull base image.
FROM phusion/baseimage:0.9.22

LABEL name="Check If You Can Get Legal Aid (cla_public)" \
      maintainer="LAA Get Access <laa-get-access@digital.justice.gov.uk>" \
      version="1.0"

ENV HOME /root

# Install python and build packages
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get -y --force-yes install \
      apt-utils \
      build-essential \
      g++ \
      git \
      libffi-dev \
      libpcre3 \
      libpcre3-dev \
      libpq-dev \
      make \
      nodejs \
      python-dev \
      python-pip \
      python-software-properties \
      software-properties-common \
      tzdata

# Set timezone
RUN ln -fs /usr/share/zoneinfo/Europe/London /etc/localtime

# Install nginx
RUN add-apt-repository ppa:nginx/stable && \
    apt-get update && \
    apt-get -y --force-yes install nginx-full && \
    chown -R www-data:www-data /var/lib/nginx && \
    rm -f /etc/nginx/sites-enabled/default && \
    mkdir -p /var/log/nginx/cla_public

# Install global Python packages
RUN pip install -U setuptools pip wheel

# Install uwsgi
RUN pip install GitPython uwsgi && \
    mkdir -p /var/log/wsgi && \
    chown -R www-data:www-data /var/log/wsgi && \
    chmod -R g+s /var/log/wsgi

ENV APP_HOME /home/app/flask
WORKDIR /home/app/flask

# Install python packages
COPY requirements.txt .
COPY requirements/ requirements/
RUN pip install -r requirements.txt

# Install npm packages
COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Compile frontend assets and translations
RUN ./node_modules/.bin/gulp build && \
    pybabel compile -d cla_public/translations

COPY ./docker/cla_public.ini /etc/wsgi/conf.d/cla_public.ini
COPY ./docker/uwsgi.service /etc/service/uwsgi/run
COPY ./docker/nginx.service /etc/service/nginx/run
COPY ./docker/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["/sbin/my_init"]
