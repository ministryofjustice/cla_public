# Installation

## Dependencies

- [Virtualenv](http://www.virtualenv.org/en/latest/)
- [Python 2.7](http://www.python.org/) (Can be installed using `brew`)
- [nodejs.org](http://nodejs.org/) (v8.12 - can be installed using [nvm](https://github.com/creationix/nvm))
- [docker](https://www.docker.com/) - Only required for running application from Docker

## Manual Installation

Clone the repository:

    git clone git@github.com:ministryofjustice/cla_public.git

Next, create the environment and start it up:

    cd cla_public
    virtualenv env --prompt=\(cla_public\)

    source env/bin/activate

    pip install -r requirements/dev.txt

    npm install -g gulp

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
