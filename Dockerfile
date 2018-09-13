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

# Dependencies
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
  apt-get -y --force-yes install apt-utils python-pip \
  python-dev build-essential git software-properties-common \
  python-software-properties libpq-dev g++ make libpcre3 libpcre3-dev libffi-dev \
  nodejs tzdata

# Set timezone
RUN ln -fs /usr/share/zoneinfo/Europe/London /etc/localtime

# Install Nginx.
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository ppa:nginx/stable && apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get -y --force-yes install nginx-full && \
  chown -R www-data:www-data /var/lib/nginx

RUN rm -f /etc/nginx/sites-enabled/default

# Pip install Python packages
RUN pip install -U setuptools pip wheel
RUN pip install GitPython uwsgi

RUN mkdir -p /var/log/wsgi && chown -R www-data:www-data /var/log/wsgi && chmod -R g+s /var/log/wsgi

COPY ./docker/cla_public.ini /etc/wsgi/conf.d/cla_public.ini
COPY ./docker/uwsgi.service /etc/service/uwsgi/run
COPY ./docker/nginx.service /etc/service/nginx/run
COPY ./docker/nginx.conf /etc/nginx/nginx.conf

# Define mountable directories.
#VOLUME ["/data", "/var/log/nginx", "/var/log/wsgi", "/var/log/cla_public"]
RUN mkdir -p /var/log/nginx/cla_public

ENV APP_HOME /home/app/flask
WORKDIR /home/app/flask

# Install python packages
COPY requirements.txt .
COPY requirements/ requirements/
RUN pip install -r requirements.txt

# Install npm and bower packages
COPY package.json package-lock.json .bowerrc bower.json ./
RUN npm install && \
    ./node_modules/.bin/bower --allow-root install

COPY . .

# Compile frontend assets and translations
RUN ./node_modules/.bin/gulp build && \
    pybabel compile -d cla_public/translations

EXPOSE 80
CMD ["/sbin/my_init"]
