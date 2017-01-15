from __future__ import unicode_literals

import math
import unicodedata
from os import path

import ephem
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from spacetrack import SpaceTrackClient

from .validators import *


def decdeg2dms(dd):
    is_positive = dd >= 0
    dd = abs(dd)
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    degrees = degrees if is_positive else -degrees
    returnstr = '%s:%s:%s'
    return returnstr % (int(degrees), int(minutes), seconds)


def satellite_upload(instance, filename):
    now = timezone.now()
    satdir = str(instance.satellite.pk)
    base, ext = path.splitext(filename)
    fn = '%s%s' % (now.strftime("%Y%m%d-%H%M%S"), ext)
    return path.join(satdir, fn)


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Satellite(BaseModel):
    norad_id = models.IntegerField(primary_key=True, verbose_name=u'NORAD catalog number')
    name = models.CharField(max_length=100)
    # https://www.space-track.org/documentation#/tle
    # blank=True in case something goes wrong getting tle from space-track on add
    tle = models.CharField(max_length=164, blank=True, verbose_name=u'two-line element')

    def update_tle(self):
        st = SpaceTrackClient(identity=settings.SPACETRACK_IDENTITY, password=settings.SPACETRACK_PASSWORD)
        tle = st.tle_latest(iter_lines=True, ordinal=1, norad_cat_id=self.pk, format='tle')
        self.tle = '\n'.join(tle)

    def update_trajectories(self):
        self.satellitetrajectory_set.all().delete()

        line1 = unicodedata.normalize('NFKD', self.name).encode('ascii', 'ignore')  # not strictly necessary
        line2, line3 = self.tle.split('\n')
        s = ephem.readtle(line1, line2, line3)

        for observer in Observer.objects.all():
            # http://rhodesmill.org/pyephem/quick
            o = ephem.Observer()
            o.lat = decdeg2dms(observer.lat)
            o.lon = decdeg2dms(observer.lon)
            o.elevation = observer.elevation
            # From documentation: Rising and setting are sensitive to atmospheric refraction at the horizon, and
            # therefore to the observer's temp and pressure; set the pressure to zero to turn off refraction.
            o.pressure = 0  # (defaults to 1010mBar)
            # o.temp (defaults to 25C)
            # o.horizon: defaults to 0, but may want to set to 34 or make observer-dependent. From documentation:
            # The United States Naval Observatory, rather than computing refraction dynamically,
            # uses a constant estimate of 34' of refraction at the horizon. To determine when a body will rise
            # "high enough" above haze or obstacles, set horizon to a positive number of degrees.
            # A negative value of horizon can be used when an observer is high off of the ground.

            o.date = o.epoch = ephem.now()
            date_limit = ephem.Date(o.date + observer.trajectory_window * ephem.hour)
            while o.date < date_limit:
                try:
                    traj = o.next_pass(s)
                    if settings.DEBUG:
                        print(o.next_pass(s))

                    st = SatelliteTrajectory()
                    st.satellite = self
                    st.observer = observer
                    st.rise_time = timezone.make_aware(traj[0].datetime(), timezone.utc)
                    st.rise_azimuth = math.degrees(traj[1])
                    st.maxalt_time = timezone.make_aware(traj[2].datetime(), timezone.utc)
                    st.maxalt_altitude = math.degrees(traj[3])
                    st.set_time = timezone.make_aware(traj[4].datetime(), timezone.utc)
                    st.set_azimuth = math.degrees(traj[5])

                    st.save()
                    o.date = o.epoch = traj[4]
                except ValueError:
                    o.date = o.epoch = date_limit
                    # TODO: handle geosynchronous satellites (no trajectories calculated)

    def save(self, *args, **kwargs):
        newsat = False
        if self._state.adding:
            newsat = True
            self.update_tle()

        super(Satellite, self).save(*args, **kwargs)

        if newsat:
            self.update_trajectories()

    def __unicode__(self):
        return '%s %s' % (self.norad_id, self.name)


class Observer(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # if we use postgres, we can use geodjango to store lat/lon as a Point
    lat = models.DecimalField(decimal_places=6, max_digits=9, verbose_name=u'latitude')
    lon = models.DecimalField(decimal_places=6, max_digits=9, verbose_name=u'longitude')
    elevation = models.IntegerField(default=0, verbose_name='elevation in meters')
    ip = models.CharField(max_length=40, default='127.0.0.1:54321')  # not currently used
    trajectory_window = models.PositiveSmallIntegerField(verbose_name='hours of trajectories', default=24)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.user.username


class SatelliteTrajectory(BaseModel):
    satellite = models.ForeignKey(Satellite)
    observer = models.ForeignKey(Observer)
    rise_time = models.DateTimeField(verbose_name=u'rise time')  # UTC
    rise_azimuth = models.DecimalField(decimal_places=6, max_digits=9, verbose_name=u'rise azimuth')
    maxalt_time = models.DateTimeField(verbose_name=u'maximum altitude time')
    maxalt_altitude = models.DecimalField(decimal_places=6, max_digits=9, verbose_name=u'maximum altitude')
    set_time = models.DateTimeField(verbose_name=u'set time')
    set_azimuth = models.DecimalField(decimal_places=6, max_digits=9, verbose_name=u'set azimuth')

    _audio = None

    # def post(self):
    #     url = self.observer.ip
    #     payload = {
    #         'norad_id': self.satellite.pk,
    #         'name': self.satellite.name,
    #         'rise_time': self.rise_time,
    #         'rise_azimuth': self.rise_azimuth,
    #         'maxalt_time': self.maxalt_time,
    #         'maxalt_altitude': self.maxalt_altitude,
    #         'set_time': self.set_time,
    #         'set_azimuth': self.set_azimuth,
    #         'audiofile': 'test',
    #         'username': 'test',
    #         'attribution': 'test'
    #     }
    #     try:
    #         r = requests.post(url, json=payload, timeout=0.001)
    #     except requests.exceptions.Timeout:
    #         pass

    # def save(self, *args, **kwargs):
    #     newtraj = False
    #     if self._state.adding:
    #         newtraj = True
    #     super(SatelliteTrajectory, self).save(*args, **kwargs)
    #     if newtraj:
    #         self.post()

    def __unicode__(self):
        return '%s %s %s' % (
            self.satellite.pk, self.observer.__unicode__(), self.rise_time.strftime(settings.TRAJECTORY_TIME_FORMAT)
        )

    class Meta:
        verbose_name_plural = 'satellite trajectories'


class SatelliteAudio(BaseModel):
    satellite = models.ForeignKey(Satellite)
    user = models.ForeignKey(User)
    attribution = models.CharField(max_length=100, blank=True)
    # if we decide we need to override filename with this pk:
    # http://stackoverflow.com/questions/651949/django-access-primary-key-in-models-filefieldupload-to-location
    audio = models.FileField(upload_to=satellite_upload, validators=[validate_audio_size, validate_audio_type])

    def __unicode__(self):
        return '%s %s' % (self.satellite.pk, self.attribution)
