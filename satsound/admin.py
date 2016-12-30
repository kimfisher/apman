from django.contrib import admin

from satsound.models import *


class SatelliteTrajectoryInline(admin.StackedInline):
    model = SatelliteTrajectory
    extra = 0


class SatelliteAudioInline(admin.StackedInline):
    model = SatelliteAudio
    extra = 1


class SatelliteAdmin(admin.ModelAdmin):
    inlines = [
        SatelliteTrajectoryInline,
        SatelliteAudioInline,
    ]


admin.site.register(Satellite, SatelliteAdmin)
admin.site.register(SatelliteTrajectory)
admin.site.register(SatelliteAudio)
admin.site.register(Observer)
