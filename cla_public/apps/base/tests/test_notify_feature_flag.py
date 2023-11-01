from cla_public.apps.base.govuk_notify.api import GovUkNotify, NotifyEmailOrchestrator
from django.test import TestCase
from mock import patch


class TestNotifyFeatureFlagEnabled(TestCase):
    @patch('cla_public.config.config.USE_EMAIL_ORCHESTRATOR_FLAG', True)
    def test_feature_flag_enabled(self):
        client = GovUkNotify()
        assert isinstance(client, NotifyEmailOrchestrator)
        assert not isinstance(client, GovUkNotify)


class TestNotifyFeatureFlagDisabled(TestCase):
    @patch('cla_public.config.config.USE_EMAIL_ORCHESTRATOR_FLAG', False)
    def test_feature_flag_disabled(self):
        client = GovUkNotify()
        assert isinstance(client, GovUkNotify)
        assert not isinstance(client, NotifyEmailOrchestrator)
