from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from spacetrack import SpaceTrackClient


# Not used now, but would be necessary if we wanted to support create/update methods
# class SatInfo(object):
#     def __init__(self, **kwargs):
#         for field in kwargs:
#             setattr(self, field, kwargs.get(field, None))


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class SatCatSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        # dynamically set fields based on whatever is passed back by the spacetrack api
        if 'instance' in kwargs and len(kwargs['instance']) > 0:
            for field in kwargs['instance'][0]:
                self.fields[field] = serializers.CharField()
                if kwargs['instance'][0][field] is not None:
                    if kwargs['instance'][0][field].isnumeric():
                        self.fields[field] = serializers.IntegerField()
                    elif is_float(kwargs['instance'][0][field]):
                        self.fields[field] = serializers.FloatField()

        super(SatCatSerializer, self).__init__(*args, **kwargs)


class SatCatViewSet(viewsets.ViewSet):
    serializer_class = SatCatSerializer
    permission_classes = []

    # Cache sattrack result for 24 hours
    @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request):
        response = ''
        if request.query_params:
            params = request.query_params.dict()
            params['metadata'] = 'false'  # required for serializer
            if 'format' in params:
                params.pop('format')
            st = SpaceTrackClient(identity=settings.SPACETRACK_IDENTITY, password=settings.SPACETRACK_PASSWORD)
            response = st.satcat(**params)

            # ?favorites=Weather&orderby=SATNAME%20asc&metadata=false
            # response = json.loads('[{"NORAD_CAT_ID": "35817", "OBJECT_NUMBER": "35817", "OBJECT_NAME": "HTV-1", "INTLDES": "2009-048A", "OBJECT_ID": "2009-048A", "RCS": "0", "RCS_SIZE": "LARGE", "COUNTRY": "JPN", "MSG_EPOCH": null, "DECAY_EPOCH": "2009-11-01 0:00:00", "SOURCE": "satcat", "MSG_TYPE": "Historical", "PRECEDENCE": "1"}, {"NORAD_CAT_ID": "37351", "OBJECT_NUMBER": "37351", "OBJECT_NAME": "HTV 2", "INTLDES": "2011-003A", "OBJECT_ID": "2011-003A", "RCS": "0", "RCS_SIZE": "LARGE", "COUNTRY": "JPN", "MSG_EPOCH": "2011-03-30 04:13:00", "DECAY_EPOCH": "2011-03-30 0:00:00", "SOURCE": "decay_msg", "MSG_TYPE": "Historical", "PRECEDENCE": "2"}]')

        serializer = SatCatSerializer(instance=response, many=True)
        return Response(serializer.data)
