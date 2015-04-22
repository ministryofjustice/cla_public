import requests
from flask import current_app


def send_email(to, subject, email_body):
    return requests.post(
        'https://api.mailgun.net/v3/{domain}/messages'.format(
            domain=current_app.config['MAILGUN_DOMAIN']
        ),
        auth=('api', 'key-{api_key}'.format(
                api_key=current_app.config['MAILGUN_API_TOKEN']
            )
        ),
        data={
            'from': 'Mailgun Sandbox <postmaster@{domain}>'.format(
                domain=current_app.config['MAILGUN_DOMAIN']
            ),
            'to': to,
            'subject': subject,
            'text': email_body
        }
    )
