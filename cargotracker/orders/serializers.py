from rest_framework import serializers

from .models import Order
from cargo.serializers import CargoSerializer
from cargo.models import Cargo


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order objects
    """

    price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            "price_per_unit_weight",
            "status",
            "past_main_branch",
            "cargo_picked_up",
            "estimated_delivery_time",
            "estimated_time_to_main_station",
            "price",
            "id",
        ]

    def validate(self, data):
        """
        Validate data.
        """
       
        # DRF pops out `cargo` because we haven't included it in the fields.
        cargo_id = self.initial_data.get("cargo")

        # Users should only handle cargo that they handled
        request = self.context.get("request")
        cargo = Cargo.objects.filter().cargo_handled_by_agent(agent=request.user).get(id=cargo_id)

        # if an order already exists for this cargo, we throw an error to the user.

        order = Order.objects.check_cargo_order(cargo)

        if order:
            raise serializers.ValidationError({"errosrs": {"cargo": "The cargo already has an order associated with it."}})

        data['cargo'] = cargo

        return super().validate(data)

    def create(self, validated_data):
        """
        Ensure that the correct methods are used to create Order
        """

        status = validated_data.get("status", "P")

        cargo = validated_data.get("cargo")
        p_per_unit_weight = validated_data.get("price_per_unit_weight")
        past_main_branch = validated_data.get("past_main_branch")

        try:
            order = Order.objects.get_or_create_order(
                cargo=cargo,
                price_per_unit_weight=p_per_unit_weight,
                past_main_branch=past_main_branch,
                status=status
            )[0]
            return self.to_representation(order)

        except TypeError as e:
            raise serializers.ValidationError({"errors": {"detail": e.args[0]}}) from e
