
============
 CLA Public
============

Installation
============

Ideally there'd be a salt state you could run to bootstrap a CLA Public dev environment, but absent that, run these commands::

  pip install -r requirements.txt

  python setup.py develop

Then, copy ``cla_public.sample.conf`` and name it ``cla_public.dev.conf`` or a name of your choosing.

Next you must tell Flask where to find your configuration file::

  export CLA_PUBLIC_CONFIG=cla_public.dev.conf

Next, you can run the management command like this::

  ./manage.py --help

You can run the server with ``manage.py runserver``.
