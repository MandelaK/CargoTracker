from django.urls import path

from .views import ListCreateOrderAPIView, RetreiveUpdateOrderAPIView

urlpatterns = [
    path(
        "<tracking_id>/",
        RetreiveUpdateOrderAPIView.as_view(),
        name="order-detail-view",
    ),
    path("", ListCreateOrderAPIView.as_view(), name="list-order"),
]
