# CLA Public

## Important notices

- `master` branch is the default branch

## Table of contents

- [**Dependencies**](#dependencies)
- [**Installation Options**](#installation)
  * [**Manual**](#manual-installation)
- [**Development**](#development)
- [**Testing**](#testing)
  * [**Unit tests**](#unit-tests)
  * [**End-to-end browser tests**](#end-to-end-browser-tests)
- [**Using Kubernetes**](#using-kubernetes)
  * [**Setup kubectl**](#setup-kubectl)
  * [**Kubernetes namespaces**](#kubernetes-namespaces)
  * [**Admin role**](#admin-role)
  * [**Authenticating with AWS ECR repository**](#authenticating-with-aws-ecr-repository)
- [**Releasing**](#testing)
  * [**Releasing to non-production**](#releasing-to-non-production)
  * [**Releasing to production**](#releasing-to-production)
    * [**Template Deploy**](#template-deploy)
    * [**Kubernetes Deploy**](#kubernetes-deploy)
- [**Monitoring**](#monitoring)
  * [**Logs**](#logs)
  
## Dependencies

- [Virtualenv](http://www.virtualenv.org/en/latest/)
- [Python 2.7](http://www.python.org/) (Can be installed using `brew`)
- [nodejs.org](http://nodejs.org/) (v8.12 - can be installed using [nvm](https://github.com/creationix/nvm))
- [docker](https://www.docker.com/) - Only required for running application from Docker

## Installation

### Manual Installation

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

With the `testing` configuration, you can use `BACKEND_BASE_URI` and `LAALAA_API_HOST`
environment variables to configure the dependent service API ports.

## Development

Assets reside in `static-src` directory and compiled in `static` directory upon running build tasks.

CLA Public is using [Gulp](http://gulpjs.com/) for build tasks. The following Gulp tasks are used in development:

- `build` builds and minifies all assets and does all of the following
- `lint` runs JS Hint on JS code
- `sass` builds the SCSS and generates source maps
- `serve` watches the files for changes and reloads the browser using [BrowserSync](http://www.browsersync.io/)

If you have [Foreman](https://github.com/ddollar/foreman) installed you can run `./tools/start-server` which will start the CLA Flask server and run the `gulp serve` process, enabling you to concentrate on the code leaving building and reloading to `serve` task.


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

## Using Kubernetes

Read the following if you want to use Kubernetes from your local development environment.

### Setup kubectl

You'll need to install and configure `kubectl` CLI tool to interact with Kubernetes. There are [instructions on kubectl configuration](https://ministryofjustice.github.io/cloud-platform-user-docs/01-getting-started/001-kubectl-config/) in the Cloud Platform User Guide.

### Kubernetes namespaces


`cla_public` has two namespaces (environments):

- [laa-cla-public-staging](https://github.com/ministryofjustice/cloud-platform-environments/tree/master/namespaces/cloud-platform-live-0.k8s.integration.dsd.io/laa-cla-public-staging)
- [laa-cla-public-production](https://github.com/ministryofjustice/cloud-platform-environments/tree/master/namespaces/cloud-platform-live-0.k8s.integration.dsd.io/laa-cla-public-production)

### Admin role

When you become a member of the GitHub team `laa-get-access`, you'll automatically get the `ClusterRole - admin` role.

>**What is the ClusterRole -admin**
>Allows admin access, intended to be granted within a namespace using a RoleBinding. If used in a RoleBinding, allows read/write access to most resources in a namespace, including the ability to create roles and rolebindings within the namespace. It does not allow write access to resource quota or to the namespace itself. https://kubernetes.io/docs/reference/access-authn-authz/rbac/#default-roles-and-role-bindings

You can [find out more about roles](https://ministryofjustice.github.io/cloud-platform-user-docs/01-getting-started/002-env-create/#01-rbacyaml) in the Cloud Platform User Guide.


### Authenticating with the Docker registry
Docker images are stored in AWS ECR. To authenticate with the `cla_public` repository, fetch the credentials by typing the following:

```
kubectl --namespace laa-cla-public-staging get secrets -o yaml
```

This command will return the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. You can find out more by reading [Authenticating with the repository](https://ministryofjustice.github.io/cloud-platform-user-docs/02-deploying-an-app/001-app-deploy/#authenticating-with-the-repository)

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

#### Template Deploy
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

#### Deploy to Kubernetes using CircleCI

**Note:** We currently have an offline production environment in Kubernetes. This will not be mapped to the public URL until further tasks have been completed.

1. Please make sure you tested on a non-production environment before merging.
1. Merge your feature branch pull request to `master`.
1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/cla_public/tree/master) for the `master` branch.
1. Approve the pending staging deployment on CircleCI (see 'Releasing to non-production above' video for more info).
1. Approve the pending production deployment on CircleCI.
1. :rotating_light: Unfortunately, our deployment process does not _yet_ fail the build if the deployment fails.
    To see if the deploy was successful, follow Kubernetes deployments, pods and events for any feedback:
    ```
    kubectl --namespace laa-cla-public-production get pods,deployments -o wide
    kubectl --namespace laa-cla-public-production get events
    ```

## Monitoring

### Logs

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
