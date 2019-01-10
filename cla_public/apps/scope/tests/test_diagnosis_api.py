# coding: utf-8
import unittest

from cla_public.app import create_app
from cla_public.apps.scope.api import diagnosis_api_client as api


class TestReviewPage(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config/testing.py")
        ctx = self.app.test_request_context()
        ctx.push()
        self.client = self.app.test_client()
        api.create_diagnosis()

    def assertResponseHasNNodes(self, resp, n):
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json().get("nodes")), n)

    def test_diagnosis_pathway(self):
        diagnosis_paths = [
            "/scope/diagnosis/",
            "/scope/diagnosis/n43n14/",
            "/scope/diagnosis/n43n14/n105/",
            "/scope/diagnosis/n43n14/n105/n106/",
            "/scope/refer/family",
        ]

        self.client.get("/start")

        for path in diagnosis_paths:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)

    def test_outcome(self):
        paths = [
            # family > disputes over children > with ex over children > domestic abuse > no immediate harm risk
            ("INSCOPE", ["n43n14", "n105", "n106", "n62", "n19"]),
            # family > disputes over children > with ex over children > domestic abuse > immediate harm risk
            ("CONTACT", ["n43n14", "n105", "n106", "n62", "n18"]),
            # family > any other problem
            ("INELIGIBLE", ["n43n14", "n53"]),
        ]

        for outcome, choices in paths:
            resp = None
            for n in range(1, len(choices) + 1):
                resp = api.move(choices[:n])

            self.assertEqual(resp.json().get("state"), outcome)

    def test_direct_link(self):
        # family > dispute over children > in a dispute with ex-partner > family mediation
        resp = api.move(["n43n14", "n105", "n106", "n59"])
        self.assertResponseHasNNodes(resp, 4)

        # family > problem with ex
        resp = api.move(["n43n14", "n51"])
        self.assertResponseHasNNodes(resp, 2)

        # family
        resp = api.move(["n43n14"])
        self.assertResponseHasNNodes(resp, 1)

        resp = api.move([])
        self.assertResponseHasNNodes(resp, 0)

    def test_steps_and_direction(self):
        steps, direction = api.get_steps_and_direction(range(6), range(3))

        self.assertEqual(steps, [5, 4, 3])
        self.assertEqual(direction, "up")

        steps, direction = api.get_steps_and_direction(range(3), range(6))

        self.assertEqual(steps, [3, 4, 5])
        self.assertEqual(direction, "down")

    def test_get_category(self):
        response_json = {"nodes": [{"label": "Domestic abuse"}], "category": None}

        self.assertEqual(api.get_category(response_json), "violence")
