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

# Set timezone
RUN echo "Europe/London" > /etc/timezone  &&  dpkg-reconfigure -f noninteractive tzdata

# Dependencies
RUN DEBIAN_FRONTEND='noninteractive' apt-get update && \
  apt-get -y --force-yes install apt-utils bash git \
  build-essential git software-properties-common \
  libpq-dev g++ make libpcre3 libpcre3-dev libffi-dev wget libxslt-dev libxml2-dev

# Install Nginx.
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository ppa:nginx/stable && apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get -y --force-yes install nginx-full && \
  chown -R www-data:www-data /var/lib/nginx


RUN apt-get clean

# Install latest python
ADD ./docker/install_python.sh /install_python.sh
RUN chmod 755 /install_python.sh
RUN /install_python.sh


RUN rm -f /etc/nginx/sites-enabled/default

# Pip install Python packages
RUN pip install -U setuptools pip wheel
RUN pip install GitPython uwsgi

RUN mkdir -p /var/log/wsgi && chown -R www-data:www-data /var/log/wsgi && chmod -R g+s /var/log/wsgi

ADD ./docker/cla_public.ini /etc/wsgi/conf.d/cla_public.ini

# install service files for runit
ADD ./docker/uwsgi.service /etc/service/uwsgi/run

# install service files for runit
ADD ./docker/nginx.service /etc/service/nginx/run

# Define mountable directories.
#VOLUME ["/data", "/var/log/nginx", "/var/log/wsgi", "/var/log/cla_public"]
RUN mkdir -p /var/log/nginx/cla_public

# Expose ports.
EXPOSE 80

# APP_HOME
ENV APP_HOME /home/app/flask

# PIP INSTALL APPLICATION
ADD ./requirements /requirements
RUN pip install -r /requirements/jenkins.txt

# Add project directory to docker
ADD ./ /home/app/flask

# awaiting docker fix
#WORKDIR /home/app/flask

# COMPILE TRANSLATION
RUN cd /home/app/flask && find . -name '*.pyc' -delete && pybabel compile -d cla_public/translations

ADD ./docker/nginx.conf /etc/nginx/nginx.conf

# RUN TESTS
RUN cd /home/app/flask && VIRTUAL_ENV=/usr/local /usr/local/bin/python manage.py test