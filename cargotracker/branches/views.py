from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status

from authentication.permissions import IsSuperUserOrReadOnly
from .serializers import BranchSerializer
from .models import Branch


class ListCreateBranchAPIView(ListCreateAPIView):
    """
    This view allows the admins to create branches and their agents.
    """

    permission_classes = [IsSuperUserOrReadOnly]
    serializer_class = BranchSerializer
    queryset = Branch.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Create a branch
        """

        response = super().create(request, *args, **kwargs)

        payload = {"data": response.data.copy()}
        payload["data"]["message"] = "Successfuly created the branch!"

        return Response(payload, status=status.HTTP_201_CREATED)
