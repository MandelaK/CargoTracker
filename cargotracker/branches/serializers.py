from rest_framework import serializers
from django.conf import settings

from cargotracker.UTILS.tasks import send_async_email
from .models import Branch
from cargotracker.UTILS.validators import validate_that_email_belongs_to_active_agent


class BranchSerializer(serializers.ModelSerializer):
    """
    Handle the logic for creating and updating branches
    """

    branch_agent = serializers.EmailField()

    class Meta:
        model = Branch
        fields = "__all__"

    def validate(self, data):
        """
        Ensure that data is valid.
        """
        agent_instance = validate_that_email_belongs_to_active_agent(
            data.get("branch_agent")
        )[1]
        data["branch_agent"] = agent_instance
        return data

    def create(self, validated_data):
        try:
            response = Branch.objects.create_branch(**validated_data)

            branch_agent = validated_data.get("branch_agent")
            subject = "Branch Assigned."
            message = f"Hello {branch_agent.username}, CargoTracker just opened a new branch in {response.city} and you have been assigned as the branch manager there. You can log in and process all orders passing through your branch."
            send_async_email(
                subject=subject,
                message=message,
                sender=settings.ADMIN_EMAIL,
                recepients=[branch_agent.email,],
            )
            return response

        except TypeError as e:
            raise serializers.ValidationError(
                {"errors": {"detail": e.args[0], "code": "invalid"}}
            ) from e
