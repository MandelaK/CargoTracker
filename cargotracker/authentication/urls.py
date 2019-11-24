from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserLoginView, logout_view, UserRegisterAPIView, AgentRegisterAPIView

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("register/", UserRegisterAPIView.as_view(), name="register-user"),
    path("agent/", AgentRegisterAPIView.as_view(), name="register-agent"),
]
