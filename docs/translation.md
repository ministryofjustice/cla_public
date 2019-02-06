# Translations

This project uses pybabel to manage strings that need translation. 

Install the Transifex client

    pip install requirements/dev.txt

Extract translatable strings

    pybabel extract -F babel.cfg -k lazy_gettext -o cla_public/translations/messages.pot .
    
Update

    pybabel update -i cla_public/translations/messages.pot -d cla_public/translations

Using the team's Transifex credentials, fetch an API token from https://www.transifex.com/user/settings/api/

Add the credentials to `~/.transifexrc`

Push to Transifex
        
    tx push --source --translations

Wait for strings to be translated

Pull from Transifex

    tx pull --force --language=cy
        
Compile the translations

    pybabel compile -d cla_public/translations

Commit translations
