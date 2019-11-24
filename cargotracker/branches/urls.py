from django.urls import path

from .views import CreateBranchAPIView

urlpatterns = [
    path("", CreateBranchAPIView.as_view(), name="create-branch"),
]
