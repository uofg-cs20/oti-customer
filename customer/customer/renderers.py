import datetime

from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.utils.encoders import JSONEncoder

# The following code is from https://github.com/encode/django-rest-framework/issues/4255

class MilliSecondEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            representation = obj.isoformat()
            if obj.microsecond:
                representation = representation[:23] + representation[26:]
            else:
                representation = representation[:19] + ".000" + representation[19:]
            if representation.endswith('+00:00'):
                representation = representation[:-6] + 'Z'
            return representation
        else:
            return super().default(obj)


class CustomJSONRenderer(JSONRenderer):
    encoder_class = MilliSecondEncoder
    