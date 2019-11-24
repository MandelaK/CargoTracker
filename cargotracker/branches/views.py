from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from authentication.permissions import IsSuperUser
from .serializers import BranchSerializer

# Create your views here.


class CreateBranchAPIView(CreateAPIView):
    """
    This view allows the admins to create branches and their agents.
    """

    permission_classes = [IsSuperUser]
    serializer_class = BranchSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a branch
        """

        response = super().create(request, *args, **kwargs)

        payload = {"data": response.data.copy()}
        payload["data"]["message"] = "Successfuly created the branch!"

        return Response(payload, status=status.HTTP_201_CREATED)
