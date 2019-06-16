from django.urls import path
from asd_rest_api import views

urlpatterns = [
    path('areas/', views.AreasList.as_view()),
    path('area/<int:pk>/', views.AreaDetail.as_view()),
    path('events/', views.EventsList.as_view()),
    path('event/<int:pk>/', views.EventDetail.as_view()),
    path('area/<int:pk>/events/', views.AreaEvents.as_view()),
    path('flight/', views.FlightStateRequest.as_view()),
    path('area/<int:pk>/start/', views.StartScan.as_view()),
    path('area/stop/', views.StopScan.as_view()),
]
