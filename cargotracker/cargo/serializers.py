from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Cargo
from branches.models import Branch
from cargotracker.UTILS.validators import validate_branch_exists_in_city


User = get_user_model()


class CargoSerializer(serializers.ModelSerializer):
    """
    Serializer to handle the Cargo serialization.
    """

    recepient = serializers.EmailField()
    destination = serializers.CharField()
    booking_station = serializers.CharField()

    class Meta:
        model = Cargo
        
        fields = "__all__"

    def validate(self, data):
        """
        Ensure all passed data is valid.
        """
        destination = validate_branch_exists_in_city(data.get("destination"))
        booking_station = validate_branch_exists_in_city(data.get("booking_station"))
        if not destination:
            raise serializers.ValidationError(
                {"errors": {"destination": "We don't have a branch in that city."}}
            )
        elif not booking_station:
            raise serializers.ValidationError(
                {"errors": {"booking_station": "We don't have a branch in that city."}}
            )

        if destination.city == booking_station.city:
            raise serializers.ValidationError(
                {"errors": {"destination": "You cannot send a parcel to the same origin."}}
            )

        data["destination"] = destination
        data["booking_station"] = booking_station

        recepient = User.objects.get_user(email=data.get("recepient"))

        if not recepient:
            raise serializers.ValidationError(
                {"detail": "There is no user registered with that email."}
            )

        data["recepient"] = recepient

        return data

    def create(self, validated_data):
        """
        Ensure that we create the Cargo using the correct method.
        """
        try:
            cargo = Cargo.objects.create_cargo(**validated_data)
            return cargo
        except TypeError as e:
            raise serializers.ValidationError(
                {"detail": e.args[0], "code": "invalid"}
            ) from e
