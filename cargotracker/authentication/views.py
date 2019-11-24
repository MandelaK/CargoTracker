from django.shortcuts import render, reverse
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import UserLoginSerializer
from cargotracker.UTILS.auth_utils import get_authentication_tokens_from_request


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
