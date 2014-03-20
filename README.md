# CLA

Frontend application for the Civil Legal Aid Tool.

## Dependencies

* [Virtualenv](http://www.virtualenv.org/en/latest/)
* [Python](http://www.python.org/) (Can be installed using `brew`)
* [Postgres](http://www.postgresql.org/)

## Installation

Clone the repository:

    git clone git@github.com:ministryofjustice/cla_frontend.git

Next, create the environment and start it up:

    virtualenv env --prompt=\(cla_fe\)

    source env/bin/activate

Install python dependencies:

    pip install -r requirements/local.txt

Start the server:

    ./manage.py runserver 8001

## Dev

Each time you start a new terminal instance you will need to run the following commands to get the server running again:

    source env/bin/activate

    ./manage.py runserver 8001

## Frontend

Assets are managed using [gulp.js](http://gulpjs.com/). To compile the assets once, after a pull for example, run:

    gulp build

### FE Dependencies

* [nodejs.org](http://nodejs.org/)
* [Sass](http://sass-lang.com/)
* [gulp.js](http://gulpjs.com/)

### Stylesheets

Stylesheets are located in `cla_frontend/assets-src/stylesheets` and are compiled into `cla_frontend/assets/stylesheets`. They are written in Sass using the `scss` syntax. To compile the stylesheets run:

    gulp sass

### Javascripts

Javascripts files are located in `cla_frontend/assets/src/javascripts` and are concatinated into `cla_frontend/assets/javascripts`. To compile the javascript files run:

    gulp js

### Images

Image are optimised and copied into the `cla_frontend/assets/images` folder using gulp. Source images should be stored in `cla_frontend/assets-src/images`. To optimise and copy images into assets run:

    gulp images

### Development

When making frequent changes to the assets you can run a gulp watch command to instantly compile any assets. To watch the source assets, run:

    gulp watch