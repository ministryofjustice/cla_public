#!/usr/bin/env python

import requests

def get_website(url):
    return requests.get(url)

if __name__ == '__main__':
    response = get_website('http://localhost:8002')

    if response.status_code == 200:
        print 'The container is up and the app returned HTTP Status Code: OK'
    else:
        print 'Error: The container returned an unexpected HTTP Status Code %d' % (response.status_code)
        exit(1)
