from rest_framework import serializers, viewsets, mixins, permissions

from ..models import SatelliteAudio


class SatelliteAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = SatelliteAudio
        fields = '__all__'


class SatelliteAudioPermission(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return True
        elif view.action in ['update', 'partial_update', 'destroy']:
            return request.user.is_authenticated() and obj.user == request.user
        else:
            return False


# subclass from viewsets.ModelViewSet if we support all/most methods
class SatelliteAudioViewset(mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Satellite audio endpoint: list and delete handled via json; get and create handled by django views;
    update not yet implemented
    """
    serializer_class = SatelliteAudioSerializer
    # TODO: filter by user, sort for server-based datatable rendering
    queryset = SatelliteAudio.objects.all()
    permission_classes = (SatelliteAudioPermission,)
