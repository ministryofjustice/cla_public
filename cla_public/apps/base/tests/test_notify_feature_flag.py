from cla_public.apps.base.govuk_notify.api import GovUkNotify, NotifyEmailOrchestrator
from mock import patch


class TestNotifyFeatureFlagEnabled:
    @patch("cla_public.config.config.USE_EMAIL_ORCHESTRATOR_FLAG", True)
    def test_feature_flag_enabled(self):
        client = GovUkNotify()
        assert isinstance(client, NotifyEmailOrchestrator)
        assert not isinstance(client, GovUkNotify)


class TestNotifyFeatureFlagDisabled:
    @patch("cla_public.config.config.USE_EMAIL_ORCHESTRATOR_FLAG", False)
    def test_feature_flag_disabled(self):
        client = GovUkNotify()
        assert isinstance(client, GovUkNotify)
        assert not isinstance(client, NotifyEmailOrchestrator)
