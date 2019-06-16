from asd_rest_api.models import *
from rest_framework import serializers


class ScanningAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanningArea
        fields = ('id', 'title', 'center_latitude', 'center_longitude', 'radius', 'created')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'created', 'entity', 'count', 'image', 'area_id')


class FlightStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightState
        fields = ('id', 'state', 'area_id', 'created')
