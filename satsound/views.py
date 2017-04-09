from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import *
from .models import *


@login_required
def index(request):
    return render(request, 'satsound/index.html')


@login_required
def satellite(request, norad_id):
    sat = {'pk': norad_id, 'name': 'not found'}
    try:
        sat = Satellite.objects.get(pk=norad_id)
    except Satellite.DoesNotExist:
        pass

    if request.method == 'POST':
        form = SatelliteAudioForm(request.POST, request.FILES)
        if form.is_valid():
            sa = SatelliteAudio()
            sa.satellite = sat
            sa.user = request.user
            sa.attribution = form.cleaned_data['attribution']
            sa.audio = request.FILES['audio']
            sa.type = form.cleaned_data['type']
            sa.save()

            return HttpResponseRedirect(reverse('index'))

    else:
        form = SatelliteAudioForm()
    return render(request, 'satsound/satellite.html', {'sat': sat, 'form': form})
