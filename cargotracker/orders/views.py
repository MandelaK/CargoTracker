from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.generics import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from .serializers import OrderSerializer
from .models import Order
from .renderers import OrderJSONRenderer
from cargo.models import Cargo
from authentication.permissions import IsStaffOrIsAuthenticatedReadOnly


class ListCreateOrderAPIView(generics.ListCreateAPIView):
    """
    Define the endpoints for creating orders.
    """

    permission_classes = (IsStaffOrIsAuthenticatedReadOnly,)
    serializer_class = OrderSerializer
    renderer_classes = (OrderJSONRenderer,)
    def get_queryset(self):
        """
        Return appropriate queryset depending on users making the request.
        """

        user = self.request.user

        if user.is_superuser:
            return Order.objects.all()
        elif user.is_staff:
            return Order.objects.filter().for_agent(agent=user)
        return Order.objects.filter().for_user(user=user)

    def create(self, request, *args, **kwargs):
        """
        Ensure that Orders are created appropriately.
        """

        data = request.data

        if not data.get("cargo"):
            return Response({"errors": {"cargo": "You must provide cargo for this order."}}, status=status.HTTP_400_BAD_REQUEST)

        cargo_id = data.get('cargo')

        if request.user.is_superuser:
            cargo = Cargo.objects.get_cargo(id=cargo_id)
        
        else:
            cargo = Cargo.objects.filter().cargo_handled_by_agent(agent=request.user).get(id=cargo_id)

        if not cargo:
            return Response({"errors": {"cargo": "Provided cargo does not exist."}}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        response = serializer.create(serializer.validated_data)

        response["message"] = "Succesfully created the order."

        return Response(response, status=status.HTTP_201_CREATED)


class RetreiveUpdateOrderAPIView(generics.RetrieveUpdateAPIView):
    """
    Contains endpoints for retreiving and updating single Order instances.
    """

    serializer_class = OrderSerializer
    permission_classes = (IsStaffOrIsAuthenticatedReadOnly,)
    renderer_classes = (OrderJSONRenderer,)
    lookup_field = 'tracking_id'
    
    def get_queryset(self):
        """
        Return appropriate queryset depending on the user making the request
        """

        user = self.request.user

        if user.is_superuser:
            return Order.objects.all()
        elif user.is_staff:
            return Order.objects.filter().for_agent(agent=user)
        return Order.objects.filter().for_user(user=user)
