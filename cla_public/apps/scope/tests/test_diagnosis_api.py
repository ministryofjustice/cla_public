# -*- coding: utf-8 -*-
import unittest

from cla_public.app import create_app
from cla_public.apps.scope.api import diagnosis_api_client as api


class TestReviewPage(unittest.TestCase):

    def setUp(self):
        self.app = create_app('config/testing.py')
        ctx = self.app.test_request_context()
        ctx.push()
        self.client = self.app.test_client()
        api.create_diagnosis()

    def assertResponseHasNNodes(self, resp, n):
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json().get('nodes')), n)

    def test_outcome(self):
        paths = [
            ('INSCOPE', ['n65::n14', 'n76', 'n82', 'n87', 'n22']),
            ('CONTACT', ['n65::n14', 'n76', 'n82', 'n87', 'n21']),
            ('INELIGIBLE', ['n65::n14', 'n76', 'n85']),
        ]

        for outcome, choices in paths:
            resp = None
            for n in range(1, len(choices) + 1):
                resp = api.move(choices[:n])

            self.assertEqual(resp.json().get('state'), outcome)

    def test_direct_link(self):
        resp = api.move(['n65::n14', 'n76', 'n82', 'n87'])
        self.assertResponseHasNNodes(resp, 4)

        resp = api.move(['n65::n14', 'n76'])
        self.assertResponseHasNNodes(resp, 2)

        resp = api.move(['n65::n14'])
        self.assertResponseHasNNodes(resp, 1)

        resp = api.move([])
        self.assertResponseHasNNodes(resp, 0)

    def test_steps_and_direction(self):
        steps, direction = api.get_steps_and_direction(
            range(6), range(3))

        self.assertEqual(steps, [5, 4, 3])
        self.assertEqual(direction, 'up')

        steps, direction = api.get_steps_and_direction(
            range(3), range(6))

        self.assertEqual(steps, [3, 4, 5])
        self.assertEqual(direction, 'down')

    def test_get_category(self):
        response_json = {
            'nodes': [{
                'label': 'Domestic violence'
            }],
            'category': None,
        }

        self.assertEqual(api.get_category(response_json), 'violence')




