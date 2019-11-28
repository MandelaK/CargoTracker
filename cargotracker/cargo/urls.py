from django.urls import path

from .views import CargoListCreateAPIView, CargoRetrieveUpdateAPIView


urlpatterns = [
    path("", CargoListCreateAPIView.as_view(), name="create-cargo"),
    path("<id>/", CargoRetrieveUpdateAPIView.as_view(), name="cargo-detail"),
]
