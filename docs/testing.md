# Testing

## Unit tests

To run Python unit tests, use the following:

    ./manage.py test

## End to end browser tests
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
