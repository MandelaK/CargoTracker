from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CargoSerializer
from authentication.permissions import IsRegularUser


class CargoCreateAPIView(CreateAPIView):
    """
    Handle the creation of cargo by users.
    """

    permission_classes = [IsRegularUser]
    serializer_class = CargoSerializer

    def create(self, request, *args, **kwargs):
        """
        Override this method to return appropriate response to users.
        """
        data = request.data.copy()

        # it's more reliable to get the sender from the Authentication headers
        data["sender"] = request.user.pk
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)

        response = serializer.data.copy()
        response["sender"] = request.user.email
        response[
            "message"
        ] = "Succesfully created your cargo. You will be notified when the agent approves your booking."

        return Response({"data": response}, status=status.HTTP_201_CREATED)
