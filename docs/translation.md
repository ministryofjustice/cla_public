# Translations

This project uses pybabel to manage strings that need translation. 

Install the Transifex client

    source env/bin/activate
    pip install requirements/dev.txt

Extract translatable strings

    pybabel extract -F babel.cfg -k lazy_gettext -o cla_public/translations/messages.pot .
    
Update

    pybabel update -i cla_public/translations/messages.pot -d cla_public/translations

Using the a Transifex account that has been added as a Project maintainer to the `cla_public` project,
fetch an API token from https://www.transifex.com/user/settings/api/

Create `~/.transifexrc` in the following format and insert the API token:

    [https://www.transifex.com]
    api_hostname = https://api.transifex.com
    hostname = https://www.transifex.com
    password = INSERT_API_TOKEN_HERE
    username = api

Push to Transifex
        
    tx push --source --translations

Wait for strings to be translated

Pull from Transifex

    tx pull --force --language=cy
        
Compile the translations

    pybabel compile -d cla_public/translations

Commit translations
