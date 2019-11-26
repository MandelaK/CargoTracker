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

        data["destination"] = destination
        data["booking_station"] = booking_station

        try:
            recepient = User.objects.get(email=data.get("recepient"))
            data["recepient"] = recepient

            return data

        except User.DoesNotExist as e:
            raise serializers.ValidationError(
                {
                    "detail": "There is no user registered with that email. Please invite them to register so that they can use our services."
                }
            ) from e

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
