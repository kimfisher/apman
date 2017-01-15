from django.conf.urls import url
from rest_framework import routers

from .resources import *
from .views import *

router = routers.DefaultRouter()
router.register(r'satellitetrajectories', FlatSatelliteTrajectoryViewset, 'satellitetrajectories')

satsound_urls = [
    url(r'^$', index, name='index'),
    url(r'^sat/(?P<norad_id>[0-9]+)/$', satellite, name='satellite'),
]
