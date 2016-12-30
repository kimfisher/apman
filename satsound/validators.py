import magic
from django.conf import settings
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError


def validate_audio_size(upload):
    size = upload.file.size
    if size > settings.MAX_AUDIOFILE_SIZE:
        raise ValidationError('Audio file size must be less than %s MB.' % (settings.MAX_AUDIOFILE_SIZE / 1024 / 1024))


def validate_audio_type(upload):
    # header-based type detection
    file_type = magic.from_buffer(upload.file.read(), mime=True)
    if file_type not in settings.AUDIO_TYPES:
        atypelist = ["'%s'" % atype for atype in settings.AUDIO_TYPES]
        raise ValidationError('Audio file type not supported. Valid types: %s' % ', '.join(atypelist))

        # TODO: use audiotools and specific codecs on server to verify
