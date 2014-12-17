import logging
import time

import statsd


logging.basicConfig()
log = logging.getLogger(__name__)


class StatsdMiddleware(object):

    def __init__(self, app, config):
        log.info('Statsd middleware started')
        self.app = app
        self.client = statsd.StatsClient(
            config['STATSD_HOST'],
            config['STATSD_PORT'],
            prefix=config['STATSD_PREFIX'])

    def __call__(self, environ, start_response):
        request_start = time.time()
        response = self.app(environ, start_response)
        ms = int((time.time() - request_start) * 1000)
        self.client.timing('{REQUEST_METHOD}.{PATH_INFO}', ms)
        return response
