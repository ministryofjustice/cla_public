# Translations

## Translation files

This project must be fully translated into Welsh.  To do this, we have two translation files which acts as a database for all translations.  

These files are

    cla_public\translations\cy\LC_MESSAGES\messages.po
    
This lists all sentences and phrases with their Welsh alternatives.

    cla_public\translations\en\LC_MESSAGES\messages.po

This file is an override, it can be used to override the English.  For the most part, this is not used.  However, there are some rare instances when the back end will return a Welsh sentence in English mode - we have used this file to revert to the English.  Otherwise this file can be ignored.  

Both translation files follow the same format.  To update or add translations, we manually edit this file.  

For example:

    msgid "Back"
    msgstr "Yn ôl"

The English (msgid) also acts as a primary key - it is identical with the english that is on the site.
The Welsh (msgstr) is returned when the language is set to Welsh.  

The English needs to match exactly - including line returns - so this might need to be spread over several lines.  
The Welsh should only ever be one line.  Whitespace at the beginning and end of the translation is ignored.

Often, there will be a line commented out above each translation, detailing which file the English can be found in.  

In the HTML files, ensure that all strings are wrapped in translation tags.  These take two forms, either can be used

    {{ _('Back') }}
    {% trans %}Back{% endtrans %}

## Translation quality

When updating the translation file, it is important to maintain the quality of the text.  

- Ensure that all text uses smart quotes (`’` instead of `'`).
- Ensure all abbreviations are wrapped in `<abbr>` tags.
- - If it isn't obvious from context, expand the abbreviations with their meaning by adding a `title` attribute (e.g. `<abbr title='Legal Aid Agency'>LAA</abbr>`).
- - The abbreviation doesn't change with Welsh, e.g. `<abbr title='Asiantaeth Cymorth Cyfreithiol'>LAA</abbr>`.

Ensure that both the English on the HTML page and the Welsh translations are of good quality.

The content designer owns the content, so if you think there is poor wording or something should be rephrased, defer to him.  He will decide whether or not the Welsh needs to be redone - but often, if neither the meaning nor the emphasis of the sentence hasn't changed, the Welsh will not need to be altered.  

## Markup in translation

If a full sentence is wrapped in an HTML tag, this should be without the trans tags.  

For example:

    <p class="govuk-body">{% trans %}Jackdaws love my big sphinx of quartz{% endtrans %}</p>

However, if the markup appears mid-sentence, this should be included in the translation.  

For example:

    {% trans %}Jackdaws love <em>my</em> big <strong>sphinx of quartz</strong>{% endtrans %}

If the markup has quotes in it, you can either escape the quotes or use single quotes.  

For example

    {% trans %}The <abbr title='Legal Aid Agency'>LAA</abbr>{% endtrans %}
    {% trans %}The <abbr title="Ministry of Justice">MoJ</abbr>{% endtrans %}

    msgid "The <abbr title='Legal Aid Agency'>LAA</abbr>"
    msgstr "Yr <abbr title='Asiantaeth Cymorth Cyfreithiol'>LAA</abbr>"

    msgid "The <abbr title=\"Ministry of Justice\">MoJ</abbr>"
    msgstr "Y <abbr title=\"Weinyddiaeth Cyfiawnder\">MoJ</abbr>"

Some characters, such as the `%` sign, cause problems.  Always use the HTML code for this symbol and any others that cause issues.  

    {% trans %}The <abbr title='Legal Aid Agency'>LAA</abbr>{% endtrans %}

### Links

Often, links appear mid sentence.  There are a number of things to consider with links.  If using the above approach, they can become ungainly, especially in the midst of long sentences.  However, this approach will still work and is sometimes required.  

    {% trans %}Click <a class='govuk-link' href='url/to/mysterious/website.html' rel='external'>here</a> to go to a mysterious website.{% endtrans %}
    
    msgid "Click <a class='govuk-link' href='url/to/mysterious/website.html' rel='external'>here</a> to go to a mysterious website."
    msgstr "Cliciwch <a class='govuk-link' href='url/to/mysterious/website.html' rel='external'>yma</a> i fynd i wefan ddirgel."

But if the website in question has a Welsh version, we should link to the Welsh in the translation

    msgid "Click <a class='govuk-link' href='url/to/mysterious/website.html' rel='external'>here</a> to go to a mysterious website."
    msgstr "Cliciwch <a class='govuk-link' href='url/to/mysterious/website.html?lang=cymraeg' rel='external'>yma</a> i fynd i wefan ddirgel."

You should check all URLs at point of translation to see if there is a Welsh version of the website you're linking to.

If there is no Welsh version to link to, then you should consider the below alternative which is easier to maintain should the URL change.





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
