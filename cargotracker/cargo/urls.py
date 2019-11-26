from django.urls import path

from .views import CargoCreateAPIView


urlpatterns = [
    path("", CargoCreateAPIView.as_view(), name="create-cargo"),
]
