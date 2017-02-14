import json


def addr(*args):
    return {
        'formatted_address': '\n'.join(args)
    }


def mock_geocoder(postcode):
    if postcode:

        if postcode == 'e181ja':
            return json.dumps([
                addr(
                    '3 Crescent Road',
                    'London',
                    'E18 1JA'),
                addr(
                    'Some other address',
                    'E18 1JA')
            ])

        if postcode == 'sw1h9aj':
            return json.dumps([
                addr(
                    'Ministry of Justice',
                    '102 Petty France',
                    'London',
                    'SW1H 9AJ')
            ])

    return json.dumps([])
