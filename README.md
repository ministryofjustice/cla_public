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

1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/cla_public) for the feature branch.
1. Approve the pending staging deployment on CircleCI.
    [Watch the how-to video:](https://www.youtube.com/watch?v=9JovuQK-XnA)<br/>
    [![How to approve staging deployments](https://img.youtube.com/vi/9JovuQK-XnA/1.jpg)](https://www.youtube.com/watch?v=9JovuQK-XnA)
1. :rotating_light: Unfortunately, our deployment process does not _yet_ fail the build if the deployment fails.
    To see if the deploy was successful, follow Kubernetes deployments, pods and events for any feedback:
    ```
    kubectl --namespace laa-cla-public-staging get pods,deployments -o wide
    kubectl --namespace laa-cla-public-staging get events
    ```

### Releasing to production

1. Please make sure you tested on a non-production environment before merging.
1. Merge your feature branch pull request to `master`.
1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/cla_public/tree/master) for the `master` branch.
1. Copy the `master.<sha>` reference from the `build` job's "Push Docker image" step. Eg:
    ```
    Pushing tag for rev [d64474359f5d] on {https://registry.service.dsd.io/v1/repositories/cla_public/tags/master.54c165b}
    ```
1. [Deploy `master.<sha>` to **prod**uction](https://ci.service.dsd.io/job/DEPLOY-cla_public/build?delay=0sec).
    * `ENVIRONMENT` is the target environment, select depending on your needs. Select `prod` for production.
    * `CONTAINER_BRANCH` is the branch that needs to be released (`master` in the above example).
    * `VERSION` is the specific 7-character prefix of the Git SHA (`54c165b` in the above example).

:tada: :shipit:

## Monitoring

### Where are the logs?

Currently, logs on our environments (staging, production) are inside the running containers, in the following folders:

- `/var/log/cla_public`
- `/var/log/nginx`
- `/var/log/wsgi`

To access these, log into the box:

```
$ ssh <your github username>@<IP address of the instance>
$ sudo docker exec -ti cla_public bash
$ tail -f /var/log/cla_public/* /var/log/nginx/* /var/log/wsgi/*
```
