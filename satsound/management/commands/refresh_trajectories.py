from django.core.management.base import BaseCommand

from satsound.models import *


class Command(BaseCommand):
    help = 'Updates satellite TLEs and replaces all trajectories'

    def add_arguments(self, parser):
        parser.add_argument('-b', '--bin', type=int, default=400,
                            help='Specify number of satellite IDs to request per query')

    def _get_bincount(self, ids, binsize):
        n, r = divmod(len(ids), binsize)
        if r > 0:
            n += 1
        return n

    def handle(self, *args, **kwargs):
        st = SpaceTrackClient(identity=settings.SPACETRACK_IDENTITY, password=settings.SPACETRACK_PASSWORD)
        ids = [s.pk for s in Satellite.objects.all()]
        bincount = self._get_bincount(ids, kwargs['bin'])

        for i in range(0, bincount):
            query_ids = ids[i * kwargs['bin']: (i + 1) * kwargs['bin']]
            self.stdout.write(str(query_ids))
            tles = st.tle_latest(iter_lines=True, ordinal=1, norad_cat_id=query_ids, format='tle')

            tle = None
            for line in tles:
                if tle is None:
                    tle = line
                else:
                    tle = '\n'.join([tle, line])
                    norad_id = int(tle[2:7])
                    try:
                        s = Satellite.objects.get(pk=norad_id)
                        s.tle = tle
                        s.save()
                        s.update_trajectories()
                    except Satellite.DoesNotExist:
                        # TODO: log this
                        self.stdout.write('%s does not exist' % norad_id)

                    tle = None
