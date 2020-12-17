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

In python files the format is slightly different

     _(u"Back")

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

    {% trans %}Zoom in up to 300&#37;{% endtrans %}

    msgid "Zoom in up to 300&#37;"
    msgstr "Zoom in up to 300&#37;"

## Links

Often, links appear mid sentence.  There are a number of things to consider with links.  If using the above approach, they can become ungainly, especially in the midst of long sentences.  However, this approach will still work and is sometimes required.  

    {% trans %}Click <a class='govuk-link' href='url/to/mysterious/website.html' rel='external'>here</a> to go to a mysterious website.{% endtrans %}
    
    msgid "Click <a class='govuk-link' href='url/to/mysterious/website.html' rel='external'>here</a> to go to a mysterious website."
    msgstr "Cliciwch <a class='govuk-link' href='url/to/mysterious/website.html' rel='external'>yma</a> i fynd i wefan ddirgel."

But if the website in question has a Welsh version, we should link to the Welsh in the translation

    msgid "Click <a class='govuk-link' href='url/to/mysterious/website.html' rel='external'>here</a> to go to a mysterious website."
    msgstr "Cliciwch <a class='govuk-link' href='url/to/mysterious/website.html?lang=cymraeg' rel='external'>yma</a> i fynd i wefan ddirgel."

You should check all URLs at point of translation to see if there is a Welsh version of the website you're linking to.

If there is no Welsh version to link to, then you should consider using a variable which is easier to maintain should the URL change.

    {% trans
        email = Element.link_same_window('mailto:civil-legal-advice@digital.justice.gov.uk', 'civil-legal-advice@digital.justice.gov.uk', **{'class': 'email'})
    %}You can contact us at {{email}}{% endtrans %}

    msgid "You can contact us at %(email)s"
    msgstr "Gallwch gysylltu â ni yn %(email)s."

## Translation quality

When updating the translation file, it is important to maintain the quality of the text.  

- Ensure that all text uses smart quotes (`’` instead of `'`).
- Ensure all abbreviations are wrapped in `<abbr>` tags.
- - If it isn't obvious from context, expand the abbreviations with their meaning by adding a `title` attribute (e.g. `<abbr title='Legal Aid Agency'>LAA</abbr>`).
- - The abbreviation doesn't change with Welsh, e.g. `<abbr title='Asiantaeth Cymorth Cyfreithiol'>LAA</abbr>`.

Ensure that both the English on the HTML page and the Welsh translations are of good quality.

The content designer owns the content, so if you think there is poor wording or something should be rephrased, defer to him.  He will decide whether or not the Welsh needs to be redone - but often, if neither the meaning nor the emphasis of the sentence has changed, the Welsh will not need to be altered.  

If you are writing in a different language (e.g. English in the Welsh translation), mark it accordingly with markup.

    msgid "This guide is also available in Welsh (<span lang='cy'>yn Cymraeg</span>)"
    msgstr "Mae’r canllaw hwn hefyd ar gael yn Saes (<span lang='en'>in English</span>)"

## One to many translations

Occasionally, a single English word required a number of Welsh translations.  This is the case with the word "Yes".  

There are four translations for "yes".

- Ie
- Ydy
- Oes
- Ydw

The word "ie" is the default word for Yes, and this is handled in the usual way:

    msgid "Yes"
    msgstr "Ie"

For all the others, we have to mark it as being used in a certain situation.  We do this with a `msgctxt` tag.

    msgctxt "There is/are"
    msgid "Yes"
    msgstr "Oes"

We then need to mark the English.  Currently this is only done in python files, it is done thus:  

    lazy_pgettext(u"There is/are", u"Yes")

At current, we only do this for **Yes** and **No**.  

| English     | Specific Mark     | Welsh       |
| ----------- | ----------------- | ----------- |
| Yes         |                   | Ie          |
| Yes         | I am              | Ydw         |
| Yes         | There is/are      | Oes         |
| Yes         | It is             | Ydy         |
| No          |                   | Na          |
| No          | I’m not           | Nac ydw     |
| No          | There is/are not  | Nac oes     |
| No          | It isn’t          | Nac ydy     |

## Edge cases

Some translations are not suited to this approach.  For these edge cases.  We can check the Welsh language cookie and manually change what is displayed.  

    {% if request.cookies.get('locale') == 'cy_GB' %}
        Gwall:
    {% else %}
        Error: 
    {% endif %}

If you use this approach, always check for Welsh, and if that returns false, assume the language is English.

## Automatic process

This project can use pybabel to manage translations.  This is a more automated approach that was used in CLA Public up until early 2020.

However, it has been found that some crucial strings are not picked up by this more automated approach, espeically those buried deeper in the code than normal.  This includes:

    msgid "This field is required."
    msgstr "Rhaid cwblhau’r maes hwn"

Since 2020, the manual process outlined above has been used to manage translations.

<details>
  <summary>Details on this process are here for those who are curious</summary>

> Install the Transifex client
> 
>     source env/bin/activate
>     pip install requirements/dev.txt
> 
> Extract translatable strings
> 
>     ./manage.py make_messages
> 
> Using the a Transifex account that has been added as a Project maintainer to the `cla_public` project, fetch an API token from https://www.transifex.com/user/settings/api/
> 
> Create `~/.transifexrc` in the following format and insert the API token:
> 
>     [https://www.transifex.com]
>     api_hostname = https://api.transifex.com
>     hostname = https://www.transifex.com
>     password = INSERT_API_TOKEN_HERE
>     token = INSERT_API_TOKEN_HERE
>     username = api
> 
> Push to Transifex
>         
>     ./manage.py push_messages
> 
> Wait for strings to be translated
> 
> Pull from Transifex
> 
>     ./manage.py pull_messages
> 
> Compile the translations
> 
>     pybabel compile -f -d cla_public/translations
> 
> Commit translations
</details>
