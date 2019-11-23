from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserLoginView, logout_view

urlpatterns = [
    path('token/', UserLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh_token'),
]