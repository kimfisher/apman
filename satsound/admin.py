from django.contrib import admin

# from django.db.models import F, ExpressionWrapper, fields
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
    list_select_related = True


class SatelliteAudioAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'user', 'type', 'reviewed', ]
    list_select_related = True


class SatelliteTrajectoryAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'observer', 'rise_time', 'rise_azimuth', 'maxalt_time', 'maxalt_altitude',
                    'set_time', 'set_azimuth', 'halfdiff', ]
    list_filter = ['observer', 'satellite', ]
    list_select_related = True

    # def get_queryset(self, request):
    #     qs = super(SatelliteTrajectoryAdmin, self).get_queryset(request)
    #     # traj_firsthalf = F('maxalt_time') - F('rise_time')
    #     # traj_secondhalf = F('set_time') - F('maxalt_time')
    #     # duration = (F('set_time') - F('maxalt_time')) - (F('maxalt_time') - F('rise_time'))
    #     # traj_firsthalf = ExpressionWrapper(F('maxalt_time') - F('rise_time'), output_field=fields.DurationField())
    #     # traj_secondhalf = ExpressionWrapper(F('set_time') - F('maxalt_time'), output_field=fields.DurationField())
    #     # duration = ExpressionWrapper(traj_secondhalf - traj_firsthalf, output_field=fields.DurationField())
    #     # duration = ExpressionWrapper((F('set_time') - F('maxalt_time')) - (F('maxalt_time') - F('rise_time')), output_field=fields.DurationField())
    #     # qs = qs.annotate(duration=traj_secondhalf - traj_firsthalf)
    #     return qs
    #
    # # number_of_orders.admin_order_field = 'order__count'

    # Calculate the difference between the first half and second half of a trajectory, to
    # determine whether Max/MSP needs to take into account. So far, the diffs are <=3s.
    # Note that to sort we'd need to solve the db-level logic attempted above.
    def halfdiff(self, obj):
        # return obj.duration
        traj_firsthalf = obj.maxalt_time - obj.rise_time
        traj_secondhalf = obj.set_time - obj.maxalt_time
        return round((traj_secondhalf - traj_firsthalf).total_seconds(), 1)

    halfdiff.short_description = u'half diff (s)'


class ObserverAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'lat', 'lon', 'timezone', 'active', ]
    readonly_fields = ('timezone',)
    list_select_related = True


admin.site.register(Satellite, SatelliteAdmin)
admin.site.register(SatelliteTrajectory, SatelliteTrajectoryAdmin)
admin.site.register(SatelliteAudio, SatelliteAudioAdmin)
admin.site.register(Observer, ObserverAdmin)
