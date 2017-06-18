from django.core.management.base import BaseCommand

from satsound.models import *


class Command(BaseCommand):
    help = 'Populates db cache of satcat info from space-track for getting info before satellite is created'

    def handle(self, *args, **kwargs):
        SatCatCache.objects.all().delete()
        st = SpaceTrackClient(identity=settings.SPACETRACK_IDENTITY, password=settings.SPACETRACK_PASSWORD)
        params = {
            'metadata': False,
            'orderby': 'NORAD_CAT_ID%20asc',
            # 'iter_lines': True
        }
        # basicspacedata/query/class/satcat/orderby/NORAD_CAT_ID%20asc/format/null/metadata/false
        response = st.satcat(**params)
        satcache = [SatCatCache(norad_id=sat['NORAD_CAT_ID'], name=sat['OBJECT_NAME']) for sat in response]
        SatCatCache.objects.bulk_create(satcache)
