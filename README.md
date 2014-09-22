# CLA

Frontend application for the Civil Legal Aid Tool.

## Dependencies

* [Virtualenv](http://www.virtualenv.org/en/latest/)
* [Python](http://www.python.org/) (Can be installed using `brew`)
* [Postgres](http://www.postgresql.org/)
* **Frontend**
* [nodejs.org](http://nodejs.org/)
* [Sass](http://sass-lang.com/) (Ruby version - minimum v3.3)
* [gulp.js](http://gulpjs.com/) (Installed globally using `npm install -g gulp`)
* [Bower](http://bower.io/) (Installed globally using `npm install -g bower`)

## Installation

Clone the repository:

    git clone git@github.com:ministryofjustice/cla_public.git

Next, create the environment and start it up:

    virtualenv env --prompt=\(cla_fe\)

    source env/bin/activate

Install python dependencies:

    pip install -r requirements/local.txt

Install Frontend dependencies libraries:

    npm install -g bower gulp

Install bower packages:

    bower install

Install node packages:

    npm install

Compile assets:

    gulp build

Start the server:

    ./manage.py runserver 8001

## Dev

Each time you start a new terminal instance you will need to run the following commands to get the server running again:

    source env/bin/activate

    ./manage.py runserver 8002

You may need to add a local.py settings file to load apps like `debug_toolbar` and `django_pdb`. An example can be found at:

    cla_frontend/settings/.example.local.py

If using the apps suggested in this file you will also need to run `pip install` on `local.txt`:

    pip install -r requirements/local.txt

## Frontend

Assets are managed using [gulp.js](http://gulpjs.com/). To compile the assets once, after a pull for example, run:

    gulp build

### Stylesheets

Stylesheets are located in `cla_public/assets-src/stylesheets` and are compiled into `cla_public/assets/stylesheets`. They are written in Sass using the `scss` syntax. To compile the stylesheets run:

    gulp sass

### Javascripts

Javascripts files are located in `cla_public/assets/src/javascripts` and are concatinated into `cla_public/assets/javascripts`. To compile the javascript files run:

    gulp js

### Images

Image are optimised and copied into the `cla_public/assets/images` folder using gulp. Source images should be stored in `cla_public/assets-src/images`. To optimise and copy images into assets run:

    gulp images

### Development

When making frequent changes to the assets you can run a gulp watch command to instantly compile any assets. To watch the source assets, run:

    gulp watch --hostname mylocal.dev --port 8001

This task synchronises browser interactions across devices (such as scrolling, filling in forms etc) as well as LiveReload CSS, images and JS. It runs as a proxy to the local web server.

The arguments are optional. `--host` is your local webserver (defaults to `localhost`) and `--port` is your local webserver's port number (defaults to `8002`).

## Testing

CasperJS is used to run basic functional/browser tests on basic DOM interactions. To run the tests, make sure you have the following dependencies:

* [Selenium](http://docs.seleniumhq.org/) (2.41.0) (Install using homebrew `brew install selenium-server-standalone`)
* [Nightwatch.js](http://nightwatchjs.org/) (~0.4.14)
* [PhantomJS](http://phantomjs.org/) (1.9.7)

To run the tests, use the following make command:

    make test

By default, tests will be run on `http://0.0.0.0:8001/`. To change this you can pass the `--url` argument on the command called in the make file. To see what command is called look at the `Makefile` at the project root.



