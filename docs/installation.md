# Installation and running

## Running locally

### Dependencies

- [Virtualenv](http://www.virtualenv.org/en/latest/)
- [Python 2.7](http://www.python.org/) (Can be installed using `brew`)
- [nodejs.org](http://nodejs.org/) (v8.12 - can be installed using [nvm](https://github.com/creationix/nvm))
- [docker](https://www.docker.com/) - Only required for running application from Docker

### Installation

Clone the repository:

    git clone git@github.com:ministryofjustice/cla_public.git

Create the python virtual environment, activate it, and install libraries in it:

    cd cla_public
    virtualenv env --prompt=\(cla_public\)

    source env/bin/activate

    pip install -r requirements/generated/requirements-dev.txt  && pip install -r requirements/generated/requirements-no-deps.txt --no-deps

Install NodeJS, packages and build the front-end assets:

    nvm install v8.12
    nvm use v8.12
    npm install -g gulp
    npm install
    gulp

Create a ``local.py`` settings file from the example file:

    cp cla_public/config/local.py.example cla_public/config/local.py

You can run the management command like this:

    ./manage.py --help

### Running

Run the server with:

    source env/bin/activate
    BACKEND_BASE_URI=http://localhost:8010 CLA_PUBLIC_CONFIG=config/local.py ./manage.py runserver

Point your browser at it: http://localhost:5000/

You can check the cla_backend service (that it relies on) is configured and responding using:

    curl http://localhost:5000/healthcheck.json

### Environment variables

These are the important env vars during development:

| name | default | notes |
|------|---------|-------|
| BACKEND_BASE_URI | http://localhost:8000 | 'cla_backend' service's base URL. Provides 'checker' API etc. If you run cla_backend locally with docker-compose then it is likely at `http://localhost:8010` |
| LAALAA_API_HOST | https://prod.laalaa.dsd.io | 'laalaa' service's base URL. Provides a legal advisor data API. |

More env vars are used in deployed environments - see <helm_deploy/cla-public/values-production.yaml>

### Config

`common.py` is used by default, and has all the common config, but is not great to development because the DEBUG = False

`local.py` is intended for development. (It's created during installation - see above.) Usage:

    CLA_PUBLIC_CONFIG=config/local.py ./manage.py runserver

`testing.py` is designed for running tests. Usage:

    CLA_PUBLIC_CONFIG=config/testing.py ./manage.py runserver

`deployment.py` is for deployed environments

## Running locally on Kubernetes

### Preparation

Our assumptions:

- Development is on a Mac. Please amend accordingly for other operating systems.
- The local Kubernetes cluster has privileges to create namespaces and permissions for everything in those namespaces.

Steps:

1. Install [Docker for Mac](https://download.docker.com/mac/stable/Docker.dmg).
1. [Enable Kubernetes](https://docs.docker.com/docker-for-mac/#kubernetes) in Docker for Mac.
1. Switch to the `docker-for-desktop` Kubernetes context:
    ```
    $ kubectl config get-contexts
    <snip, for reference>

    $ kubectl config set-context docker-for-desktop
    ```

### Running

1. Build a local Docker image:
    ```
    $ docker build --tag=cla_public_local .
    ```
1. Deploy to local Kubernetes cluster:
    ```
    $ ECR_DEPLOY_IMAGE=cla_public_local .circleci/deploy_to_kubernetes development
    ```
1. Wait for the pod to be up:
    ```
    $ kubectl get pods
    NAME                              READY   STATUS    RESTARTS   AGE
    laa-cla-public-6b8fd56bbd-mph26   1/1     Running   0          44s
    ```
1. Find out the local port from the service:
    ```
    $ kubectl get services
    NAME             TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
    kubernetes       ClusterIP   10.96.0.1        <none>        443/TCP        7h
    laa-cla-public   NodePort    10.106.138.234   <none>        80:30000/TCP   2m
    ```
1. Open the service on the port above. In this example, the service is running on http://localhost:30000.
1. For debugging, please see the [monitoring section](monitoring.md) of the documentation.

### Re-building

1. Re-build the local Docker image:
    ```
    $ docker build --tag=cla_public_local .
    ```
1. Remove the previous pod(s) and deployment:
    ```
    $ kubectl delete deployment.apps/laa-cla-public
    deployment.apps "laa-cla-public" deleted
    ```
1. Deploy again:
    ```
    $ ECR_DEPLOY_IMAGE=cla_public_local .circleci/deploy_to_kubernetes development
    ```
