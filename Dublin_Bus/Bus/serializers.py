from rest_framework import serializers
from .models import Trip, StopTime, Route


class StopTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StopTime
        fields = ['arrival_time', 'stop_headsign', 'stop_id', 'stop_sequence', 'trip_id']
        depth = 2
