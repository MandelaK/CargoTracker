from django.shortcuts import render, reverse
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView

from .serializers import (
    UserLoginSerializer,
    AgentRegistrationSerializer,
    UserRegistrationSerializer,
)
from cargotracker.UTILS.auth_utils import get_authentication_tokens_from_request
from authentication.permissions import IsSuperUser


class UserLoginView(TokenObtainPairView):
    """
    This is the login view. Accept user input and return success or error message depending on the result of attempted authentication.
    """

    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        # This only contains token information and no useful information to user
        response = super().post(request, *args, **kwargs)

        # Add some message and context to the response payload
        payload = {"data": response.data.copy()}
        payload["data"][
            "message"
        ] = "Succesfully logged you in. Welcome to CargoTracker!"

        return Response(payload, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout_view(request):
    """
    This view invalidates the current `refresh` tokens so that users may not use them to make authenticated requests.
    """

    try:
        auth_tokens = get_authentication_tokens_from_request(request)
        refresh_token_instance = RefreshToken(auth_tokens.get("refresh"))
        refresh_token_instance.blacklist()

        next_url = request.query_params.get("next") if request.query_params else ""

        response = {
            "data": {
                "message": "You have been successfully logged out.",
                "next_url": next_url,
            }
        }
        return Response(response, status=status.HTTP_200_OK)

    except TokenError:
        return Response(
            {"errors": {"detail": "You are already logged out"}},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserRegisterAPIView(CreateAPIView):
    """
    This class controls the flow for registering users
    """

    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        Method that makes the call to save the user.
        """

        response = super().create(request, *args, **kwargs)
        payload = {"data": response.data.copy()}
        payload["data"][
            "message"
        ] = "Succesfully signed you up. You can now log into the application."

        return Response(payload, status=status.HTTP_201_CREATED)


class AgentRegisterAPIView(CreateAPIView):
    """
    This class contains logic for the creation of Branch Agents.
    """

    serializer_class = AgentRegistrationSerializer

    permission_classes = [IsSuperUser]

    def create(self, request, *args, **kwargs):
        """
        Logic for creating agents.
        """

        response = super().create(request, *args, **kwargs)
        payload = {"data": response.data.copy()}
        agent_email = payload["data"].get("email")
        payload["data"][
            "message"
        ] = f"Succesfully created the agent. Login credentials have been sent to {agent_email}."

        return Response(payload, status=status.HTTP_201_CREATED)
