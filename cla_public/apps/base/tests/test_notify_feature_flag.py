from cla_public.apps.base.govuk_notify.api import GovUkNotify, NotifyEmailOrchestrator
from django.test import TestCase
from cla_public.config import common


class TestNotifyFeatureFlagEnabled(TestCase):
    def test_feature_flag_enabled(self):
        common.USE_EMAIL_ORCHESTRATOR_FLAG = True
        client = GovUkNotify()
        assert isinstance(client, NotifyEmailOrchestrator)
        assert not isinstance(client, GovUkNotify)


class TestNotifyFeatureFlagDisabled(TestCase):
    def test_feature_flag_disabled(self):
        common.USE_EMAIL_ORCHESTRATOR_FLAG = False
        client = GovUkNotify()
        assert isinstance(client, GovUkNotify)
        assert not isinstance(client, NotifyEmailOrchestrator)
