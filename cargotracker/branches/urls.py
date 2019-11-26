from django.urls import path

from .views import ListCreateBranchAPIView

urlpatterns = [
    path("", ListCreateBranchAPIView.as_view(), name="create-branch"),
]
