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
    sat = None
    newsat = False
    try:
        if norad_id.isdigit():
            sat = Satellite.objects.get(pk=norad_id)
    except Satellite.DoesNotExist:
        newsat = True
        st = SpaceTrackClient(identity=settings.SPACETRACK_IDENTITY, password=settings.SPACETRACK_PASSWORD)
        # https://www.space-track.org/basicspacedata/query/class/satcat/NORAD_CAT_ID/3/orderby/INTLDES asc/metadata/false
        params = {
            'norad_cat_id': norad_id,
            'metadata': False
        }
        response = st.satcat(**params)

        if len(response) == 1:
            sat = Satellite(
                norad_id=norad_id,
                name=response[0].get('OBJECT_NAME', '')
            )

    status = 200
    if request.method == 'POST':
        form = SatelliteAudioForm(request.POST, request.FILES)
        if form.is_valid():
            sa = SatelliteAudio()
            if newsat:
                sat.save()
            sa.satellite = sat
            sa.user = request.user
            sa.attribution = form.cleaned_data['attribution']
            sa.audio = request.FILES['audio']
            sa.type = form.cleaned_data['type']
            sa.save()

            return HttpResponseRedirect(reverse('index'))

        else:
            status = 422  # signal error to UploadProgress

    else:
        form = SatelliteAudioForm()
    return render(request, 'satsound/satellite.html', {'sat': sat, 'form': form, 'norad_id': norad_id}, status=status)
