# Translations

This project uses pybabel to manage strings that need translation. 

Install the Transifex client

    source env/bin/activate
    pip install requirements/dev.txt

Extract translatable strings

    ./manage.py make_messages

Using the a Transifex account that has been added as a Project maintainer to the `cla_public` project,
fetch an API token from https://www.transifex.com/user/settings/api/

Create `~/.transifexrc` in the following format and insert the API token:

    [https://www.transifex.com]
    api_hostname = https://api.transifex.com
    hostname = https://www.transifex.com
    password = INSERT_API_TOKEN_HERE
    token = INSERT_API_TOKEN_HERE
    username = api

Push to Transifex
        
    ./manage.py push_messages

Wait for strings to be translated

Pull from Transifex

    ./manage.py pull_messages
        
Compile the translations

    pybabel compile -f -d cla_public/translations

Commit translations
