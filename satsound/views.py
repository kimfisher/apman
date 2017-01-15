from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import *


def index(request):
    return render(request, 'satsound/index.html')


@login_required
def satellite(request, norad_id):
    sat = {'pk': norad_id, 'name': 'not found'}
    try:
        sat = Satellite.objects.get(pk=norad_id)
    except Satellite.DoesNotExist:
        pass

    return render(request, 'satsound/satellite.html', {'sat': sat})
