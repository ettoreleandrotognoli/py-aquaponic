import json

import jsonfield
from rest_framework.serializers import Field as FieldSerializer
from rest_framework.serializers import ModelSerializer


class JSONFieldSerializer(FieldSerializer):
    def __init__(self, *args, **kwargs):
        super(JSONFieldSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        return json.loads(obj)

    def to_internal_value(self, data):
        return data


serializer_field_mapping = {
    jsonfield.JSONField: JSONFieldSerializer
}

ModelSerializer.serializer_field_mapping.update(serializer_field_mapping)
