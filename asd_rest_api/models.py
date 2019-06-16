from django.db import models
from asd_drone import constants


class ScanningArea(models.Model):
    title = models.CharField(max_length=100, blank=False, default='')
    created = models.DateTimeField(auto_now_add=True)
    center_latitude = models.CharField(max_length=100, blank=False, default='')
    center_longitude = models.CharField(max_length=100, blank=False, default='')
    radius = models.IntegerField()

    class Meta:
        ordering = ('-created',)


class Event(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    entity = models.CharField(max_length=100, blank=False, default='')
    count = models.IntegerField(default=0)
    image = models.ImageField(blank=True, null=True)
    area_id = models.IntegerField()

    class Meta:
        ordering = ('-created',)


class FlightState(models.Model):
    state = models.CharField(max_length=100, blank=False, default=constants.STATE_LANDED)
    area_id = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
