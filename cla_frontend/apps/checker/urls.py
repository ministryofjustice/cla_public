from django.conf.urls import patterns, url

from . import views


checker_wizard = views.CheckerWizard.as_view(
    url_name='checker:checker_step'
)

urlpatterns = patterns('',
    url(r'^confirmation/$', views.ConfirmationView.as_view(), name='confirmation'),

    url(r'^$', checker_wizard, name='checker'),
    url(r'^(?P<step>.+)/$', checker_wizard, name='checker_step'),
)
