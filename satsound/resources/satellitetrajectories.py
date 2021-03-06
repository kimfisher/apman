import datetime
from random import randint

import django_filters
import pytz
from rest_framework import serializers, viewsets

from ..models import *


class FlatSatelliteTrajectorySerializer(serializers.ModelSerializer):
    norad_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    rise_time = serializers.SerializerMethodField()
    maxalt_time = serializers.SerializerMethodField()
    set_time = serializers.SerializerMethodField()
    audiofile = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    attribution = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    reviewed = serializers.SerializerMethodField()

    def _choose_audio(self, obj):
        if obj._audio is None:
            audios = obj.satellite.satelliteaudio_set.filter(reviewed=True).order_by('-updated')
            if audios.count() > 0:
                # observer_window = datetime.timedelta(hours=int(obj.observer.trajectory_window))
                # recent_window = timezone.now() - observer_window

                # if most recent audio is within one hour of this trajectory's rise time, use it
                imminence = abs((audios[0].updated - obj.rise_time).total_seconds() / 3600)
                if imminence < settings.MAX_IMMINENCE:
                    obj._audio = audios[0]
                # otherwise, pick randomly
                else:
                    random_index = randint(0, audios.count() - 1)
                    obj._audio = audios[random_index]

        return obj._audio

    def _get_type_by_id(self, obj):
        ret = None
        for type in SatelliteAudio.TYPES:
            if obj._audio.type == type[0]:
                ret = type[1]

        return ret

    def get_norad_id(self, obj):
        return obj.satellite.pk

    def get_name(self, obj):
        return obj.satellite.name

    def _get_localtime(self, obj, time):
        tz = pytz.timezone(obj.observer.timezone)
        return time.astimezone(tz)

    def get_rise_time(self, obj):
        observer_rise_time = self._get_localtime(obj, obj.rise_time)
        return observer_rise_time.strftime(settings.TRAJECTORY_TIME_FORMAT)

    def get_maxalt_time(self, obj):
        observer_maxalt_time = self._get_localtime(obj, obj.maxalt_time)
        return observer_maxalt_time.strftime(settings.TRAJECTORY_TIME_FORMAT)

    def get_set_time(self, obj):
        observer_set_time = self._get_localtime(obj, obj.set_time)
        return observer_set_time.strftime(settings.TRAJECTORY_TIME_FORMAT)

    def get_audiofile(self, obj):
        ret = None
        self._choose_audio(obj)
        if obj._audio is not None:
            ret = obj._audio.audio.name
        return ret

    def get_username(self, obj):
        ret = None
        self._choose_audio(obj)
        if obj._audio is not None:
            ret = obj._audio.user.username
        return ret

    def get_attribution(self, obj):
        ret = None
        self._choose_audio(obj)
        if obj._audio is not None:
            ret = obj._audio.attribution
        return ret

    def get_type(self, obj):
        ret = None
        self._choose_audio(obj)
        if obj._audio is not None:
            ret = self._get_type_by_id(obj)
        return ret

    def get_reviewed(self, obj):
        ret = None
        self._choose_audio(obj)
        if obj._audio is not None:
            ret = obj._audio.reviewed
        return ret

    class Meta:
        model = SatelliteTrajectory
        fields = (
            'norad_id',
            'name',
            'rise_time',
            'rise_azimuth',
            'maxalt_time',
            'maxalt_altitude',
            'set_time',
            'set_azimuth',
            'audiofile',
            'username',
            'attribution',
            'type',
            'reviewed',
        )


class FlatSatelliteTrajectoryFilter(django_filters.FilterSet):
    observer = django_filters.ModelChoiceFilter(required=True, queryset=Observer.objects.all())
    rise_time_window = django_filters.NumberFilter(name='rise_time', method='trajectory_window',
                                                   label='Rise time window')

    def trajectory_window(self, queryset, name, value):
        lookup = '__'.join([name, 'range'])
        start = timezone.now()
        end = start + datetime.timedelta(seconds=int(value))

        return queryset.filter(**{lookup: (start, end)})

    class Meta:
        model = SatelliteTrajectory
        fields = ['observer', 'satellite', 'rise_time_window', ]


class FlatSatelliteTrajectoryViewset(viewsets.ReadOnlyModelViewSet):
    """Flattened read-only satellite trajectories for consumption by Max/MSP,
    filtered by: observer (required), satellite, rise time window (in seconds from now)"""
    serializer_class = FlatSatelliteTrajectorySerializer
    filter_class = FlatSatelliteTrajectoryFilter

    def get_queryset(self):
        # always limit by x # of seconds from now
        # start = timezone.now()
        # end = start + datetime.timedelta(seconds=30)
        # trajectories = SatelliteTrajectory.objects.filter(rise_time__range=(start, end)).order_by('rise_time')
        trajectories = SatelliteTrajectory.objects.all().order_by('rise_time')
        return trajectories
