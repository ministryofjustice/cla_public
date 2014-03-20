from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext



@login_required
def dashboard(request):
    return render_to_response('call_centre/dashboard.html', {}, RequestContext(request))
