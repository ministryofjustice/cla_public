#
# CLA Dockerfile
#
# https://github.com/dockerfile/nginx
#
# Pull base image.
FROM phusion/baseimage:0.9.11

MAINTAINER Peter Idah <peter.idah@digital.justice.gov.uk>

# Set correct environment variables.
ENV HOME /root
# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

# Dependencies
RUN DEBIAN_FRONTEND='noninteractive' apt-get update && \
  apt-get -y --force-yes install apt-utils python-pip \
  python-dev build-essential git software-properties-common \
  python-software-properties libpq-dev g++ make libpcre3 libpcre3-dev

# Install Nginx.
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository ppa:nginx/stable && apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get -y --force-yes install nginx-full

#ADD ./docker/nginx.conf /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/sites-enabled/default

# Install ruby
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository ppa:brightbox/ruby-ng && apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get install -y --no-install-recommends  ruby2.1 ruby2.1-dev

RUN gem2.1 install sass --no-rdoc --no-ri

# INstall Node.js
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository -y ppa:chris-lea/node.js && apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get purge -y  g++ make &&  apt-get install -y nodejs

#Pip install Python packages

RUN pip install GitPython uwsgi

RUN mkdir -p /var/log/wsgi /var/log/nginx/cla_public /root/.ssh && chown -R www-data:www-data /var/lib/nginx /var/log/wsgi

ADD ./docker/cla_public.ini /etc/wsgi/conf.d/cla_public.ini

# install service files for runit
ADD ./docker/uwsgi.service /etc/service/uwsgi/run

# install service files for runit
ADD ./docker/nginx.service /etc/service/nginx/run

# Define mountable directories.
VOLUME ["/data", "/var/log/nginx", "/var/log/wsgi"]

# Expose ports.
EXPOSE 80

# APP_HOME
ENV APP_HOME /home/app/django

# Add project directory to docker
ADD ./ /home/app/django
#
# Add local.py for QA
#RUN ln -sf  /home/app/django/cla_public/settings/integration.py /home/app/django/cla_public/settings/local.py

# Add deploy-key
ADD ./docker/deploy-key /root/.ssh/id_rsa
ADD ./docker/config /root/.ssh/config

# Define working directory.
WORKDIR /home/app/django

# PIP INSTALL APPLICATION
RUN pip install -r requirements/production.txt

#NPM bower and gulp
RUN  npm install -g bower gulp && npm install

# gulp build
RUN export LANG='en_US.UTF-8' && gulp build 

RUN locale-gen --purge  en_US.UTF-8 && echo export LANG=''

ADD ./docker/rc_script /etc/rc.local

ADD ./docker/nginx.conf /etc/nginx/nginx.conf
