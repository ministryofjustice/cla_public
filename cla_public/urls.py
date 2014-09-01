# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

urlpatterns = patterns('',
    url(r'^', include('checker.urls', namespace='checker',)),
    url(r'session_security/', include('session_security.urls')),
    ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
