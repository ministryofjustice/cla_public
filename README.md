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

    CLA_PUBLIC_CONFIG=config/testing.py ./manage.py runserver

With the `testing` configuration, you can use `CLA_BACKEND_PORT` and `LAALAA_PORT`
environment variables to configure the dependent service API ports.


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

### Unit tests

To run Python unit tests, use the following:

    ./manage.py test

### End to end browser tests
The browser tests reside in https://github.com/ministryofjustice/laa-cla-e2e-tests. Follow the instructions to get these running on your local machine.

TODO: Make these tests run automatically when a new build of the `develop` branch is pushed to Docker registry.

If you want to run the tests whilst developing, you'll need to update `docker-compose.yml` from:

```
cla_public:
    image: [url_to_remote_image]
```

to something like:

```
cla_public:
    build:
        context: ../cla_public
```

where the `context` directory is set to the root of the cla_public directory.

## Releasing

### Releasing to non-production

1. Check that [the Docker build on Jenkins](https://ci.service.dsd.io/view/CLA/job/BUILD-cla_public/) has finished for the branch that needs to be released.
1. Once finished, [deploy the branch to an environment](https://ci.service.dsd.io/view/CLA/job/DEPLOY-cla_public/build?delay=0sec).
    * `ENVIRONMENT` is the target environment, select depending on your needs, eg. "demo", "staging", etc.
    * `CONTAINER_BRANCH` is the branch that needs to be released.
    * `VERSION` is either `latest` for the last successful build on that branch, or a specific 7-character prefix of the Git SHA, eg. `35b275a`.

### Releasing to production

1. [Create a pull request](https://github.com/ministryofjustice/cla_public/compare/master...develop) to merge the `develop` branch into the `master` branch.
1. Wait for reviews and tests to all pass.
1. Merge the pull request. (Please do not delete the `develop` branch.)
1. Start [the Docker build on Jenkins](https://ci.service.dsd.io/view/CLA/job/BUILD-cla_public/build?delay=0sec) for the `master` branch.
1. Once finished, [deploy `master` to **staging**](https://ci.service.dsd.io/view/CLA/job/DEPLOY-cla_public/build?delay=0sec).
1. Check that the deploy was successful and staging contains the changes.
1. [Deploy `master` to **prod**uction](https://ci.service.dsd.io/view/CLA/job/DEPLOY-cla_public/build?delay=0sec).

:tada: :shipit:
