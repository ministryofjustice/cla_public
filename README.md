# CLA Public

## Installation

Clone the repository:

    git clone git@github.com:ministryofjustice/cla_public.git

Next, create the environment and start it up:

    cd cla_public
    virtualenv env --prompt=\(cla_public\)

    source env/bin/activate

    pip install -r requirements/local.txt

    npm install && bower install && gulp

Create a ``local.py`` settings file from the example file:

    cp cla_public/config/local.py.example cla_public/config/local.py

Next, you can run the management command like this:

    ./manage.py --help

You can run the server with:

    ./manage.py runserver

*OR*

    tools/start-dev

to run the server with foreman, which will monitor and
automatically reload CSS and JS changes and enables other whizzy things.


## Development

Assets reside in `static-src` directory and compiled in `static` directory upon running build tasks.

CLAP is using [Gulp](http://gulpjs.com/) for build tasks. The following Gulp tasks are used in development:

- `build` builds and minifies all assets and does all of the following
- `lint` runs JS Hint on JS code
- `sass` builds the SCSS and generates source maps
- `serve` watches the files for changes and reloads the browser using [BrowserSync](http://www.browsersync.io/)

If you have [Foreman](https://github.com/ddollar/foreman) installed you can run `./tools/start-server` which will start the CLA Flask server
and run the `gulp serve` process, enabling you to concentrate on the code leaving building and reloading
to `serve` task.


## Testing

To run Python unit tests, use the following:

    ./manage.py test

To set up for running tests

    npm run update-selenium

(At the moment Jenkins requires npm package selenium-standalone@~4.4 which in turn installs 2.45.0-server.jar and 2.15-x64-chromedriver. These versions seem to run the tests successfully with firefox version 34.0, which must be installed on the Jenkins server)

To run the NIghtwatch automated tests in PhantomJS use:

    make test

This command accepts two parameters:

 - `browser` - `chrome`, `firefox`, `default` (Phantom JS)
 - `spec` - name of the spec file to run (within `tests/nightwatch/specs/` directory)

Example:

    make test browser=chrome spec=review-page

Please see the `Makefile` for other commands.

## Releasing

### Releasing to production

1. [Create a pull request](https://github.com/ministryofjustice/cla_public/compare/master...develop) to merge the `develop` branch into the `master` branch.
1. Wait for reviews and tests to all pass.
1. Merge the pull request. (Please do not delete the `develop` branch.)
1. Start [the Docker build on Jenkins](https://ci.service.dsd.io/view/CLA/job/BUILD-cla_public/build?delay=0sec) for the `master` branch.
1. Once finished, [deploy `master` to **staging**](https://ci.service.dsd.io/view/CLA/job/DEPLOY-cla_public/build?delay=0sec).
1. Check that the deploy was successful and staging contains the changes.
1. [Deploy `master` to **prod**uction](https://ci.service.dsd.io/view/CLA/job/DEPLOY-cla_public/build?delay=0sec).

:tada: :shipit:
