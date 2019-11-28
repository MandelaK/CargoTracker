from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status


from authentication.models import User

from .serializers import CargoSerializer
from .models import Cargo
from .renderers import CargoJSONRenderer
from authentication.permissions import IsStaffOrIsAuthenticatedReadOnly
from branches.models import Branch


class CargoListCreateAPIView(ListCreateAPIView):
    """
    Handle the creation of cargo and also listing of multiple cargo.
    """

    permission_classes = [IsStaffOrIsAuthenticatedReadOnly]
    serializer_class = CargoSerializer
    renderer_classes = (CargoJSONRenderer,)

    def get_queryset(self):
        """
        Return different queryset depending on the user making the request.
        """

        user = self.request.user
        if user.is_superuser:
            return Cargo.objects.all()
        elif user.is_staff:
            return Cargo.objects.filter().cargo_handled_by_agent(agent=user)
        return Cargo.objects.filter().all_cargo_for_user(user=user)

    def create(self, request, *args, **kwargs):
        """
        Override this method to return appropriate response to users.
        """
        data = request.data.copy()

        sender = User.objects.get_user(email=data.get("sender"))
        destination = Branch.objects.search_by_city_exact(city=data.get("destination"))
        clearing_agent = destination.branch_agent
        if not destination:
            return Response(
                {"errors": {"city": "We don't have a branch in that city."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not sender:
            return Response(
                {
                    "errors": {
                        "sender": "We don't have a registered user by that email address"
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # we would rather get this from the user making the current request
        booking_agent = request.user
        data["booking_agent"] = booking_agent.id
        data["clearing_agent"] = clearing_agent.id

        data["sender"] = sender.id

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.create(serializer.validated_data)

        response = serializer.data.copy()
        response["message"] = "Succesfully created cargo."

        return Response({"data": response}, status=status.HTTP_201_CREATED)


class CargoRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    Endpionts for displaying single Cargo and also updating it.
    """

    permission_classes = [IsStaffOrIsAuthenticatedReadOnly]
    serializer_class = CargoSerializer
    lookup_field = "id"
    renderer_classes = (CargoJSONRenderer,)

    def get_queryset(self):
        """
        We will need a different queryset depending on the user who is making the request
        """
        user = self.request.user
        if user.is_superuser:
            return Cargo.objects.all()
        elif user.is_staff:
            return Cargo.objects.filter().cargo_handled_by_agent(agent=user)
        return Cargo.objects.filter().all_cargo_for_user(user=user)

    def patch(self, request, *args, **kwargs):
        """
        Allow updates to the Cargo.
        """
        data = request.data

        # ensure that sensitive fields are never updated.

        read_only_during_update = ('booking_agent', 'weight', 'sender', 'title')
        [data.pop(key) for key in data.copy().keys() if key in read_only_during_update]

        obj = self.get_object()

        if data.get("destination"):
            destination = Branch.objects.search_by_city_exact(data.get('destination'))
            if not destination:
                return Response({"errors": {"destination": "We have no branch in that city."}})

            # If the destination changes, ensure also that the clearing_agent changes

            data['clearing_agent'] = destination.branch_agent.id
            data['destination'] = destination.city

        else:  
            data['destination'] = obj.destination.city

        if not data.get("recepient"):
            data['recepient'] = obj.recepient.email
        
        data['booking_station'] = obj.booking_station.city

        response = super().patch(request, *args, **kwargs)

        payload = response.data
        payload['message'] = 'Succesfully perfomed necessary updates.'

        return Response(payload, status=status.HTTP_200_OK)
