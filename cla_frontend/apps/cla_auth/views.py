from django.core.urlresolvers import reverse


def login_redirect_url(request):
    return reverse('call_centre:dashboard')
