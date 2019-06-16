from asd_rest_api.models import ScanningArea, Event, FlightState
from asd_rest_api.serializers import ScanningAreaSerializer, EventSerializer, FlightStateSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from asd_drone import constants
from asd_drone.flight_control import FlightControl


class AreasList(APIView):
    """
    List all areas, or create a new area.
    """
    def get(self, request, format=None):
        areas = ScanningArea.objects.all()
        serializer = ScanningAreaSerializer(areas, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = ScanningAreaSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AreaDetail(APIView):
    """
    Retrieve, update or delete a area instance.
    """
    def get_object(self, pk):
        try:
            return ScanningArea.objects.get(pk=pk)
        except ScanningArea.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        area = self.get_object(pk)
        serializer = ScanningAreaSerializer(area)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        area = self.get_object(pk)
        serializer = ScanningAreaSerializer(area, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        area = self.get_object(pk)
        area.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventsList(APIView):
    """
    List all events, or create a new event.
    """
    def get(self, request, format=None):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDetail(APIView):
    """
    Retrieve, update or delete a event instance.
    """
    def get_object(self, pk):
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        event = self.get_object(pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        event = self.get_object(pk)
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        event = self.get_object(pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AreaEvents(APIView):
    """
        List all events of an area_id.
    """
    def get_area(self, pk):
        try:
            return ScanningArea.objects.get(pk=pk)
        except ScanningArea.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        area = self.get_area(pk)
        events = Event.objects.filter(area_id=area.id)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)


class FlightStateRequest(APIView):
    """
    Retreive current flight state
    """
    def get_flight_state(self):
        state = FlightState.objects.first()

        if state is None:
            raise Http404
        else:
            return state

    def get(self, request, format=None):
        state = self.get_flight_state()
        serializer = FlightStateSerializer(state)
        return Response(serializer.data)


class StartScan(APIView):
    """
    Manage action for start scanning
    """
    def delete_flight_states(self):
        FlightState.objects.all().delete()

    def create_flight_state(self, area):
        state = FlightState(area_id=area.id)
        state.state = constants.STATE_STARTING
        state.save()
        return state

    def get_area(self, pk):
        try:
            return ScanningArea.objects.get(pk=pk)
        except ScanningArea.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        area = self.get_area(pk)
        self.delete_flight_states()
        flight_state = self.create_flight_state(area)

        flight_control = FlightControl()
        flight_control.async_start()

        serializer = FlightStateSerializer(flight_state)
        return Response(serializer.data)


class StopScan(APIView):
    """
    Manage action for stop scanning
    """
    def get_flight_state(self):
        state = FlightState.objects.first()

        if state is None:
            raise Http404
        else:
            return state

    def get(self, request, format=None):
        flight_state = self.get_flight_state()
        flight_state.state = constants.STATE_STOPPING
        flight_state.save(update_fields=['state'])
        serializer = FlightStateSerializer(flight_state)
        return Response(serializer.data)
