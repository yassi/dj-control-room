from django.urls import path
from . import views

app_name = "dj_control_room"

urlpatterns = [
    path("", views.index, name="index"),
]
