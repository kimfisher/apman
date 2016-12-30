from rest_framework import routers

from .resources import *

router = routers.DefaultRouter()

router.register(r'satellitetrajectories', FlatSatelliteTrajectoryViewset, 'satellitetrajectories')
