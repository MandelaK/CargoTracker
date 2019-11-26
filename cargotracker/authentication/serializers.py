from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from .models import User


class UserLoginSerializer(TokenObtainPairSerializer):
    """
    This serializer functions as our login serializer. It accepts user input and attempts to validate it and return valid access and refresh tokens if the email and password are correct.
    """

    @classmethod
    def get_token(cls, user):
        """
        Override this method to ensure that the email address is encoded within the JWT token.
        """
        token = super().get_token(user)

        token["email"] = user.email

        return token


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    The serializer class that validates and saves user data before registration
    """

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "last_name", "first_name"]

    def create(self, validated_data):
        """
        Create and save user instances if we have valid data.
        """
        try:
            user = User.objects.create_user(**validated_data)
            return user

        except TypeError as e:
            raise serializers.ValidationError(
                {"errors": {"detail": e.args[0], "code": "invalid"}}
            )


class AgentRegistrationSerializer(serializers.ModelSerializer):
    """
    Contain the serializer for creating branch agents.
    """

    is_staff = serializers.BooleanField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "is_staff"]

    def create(self, validated_data):
        """
        Override this method so that we call the `create_branch_agent` manager method instead.
        """

        try:
            agent = User.objects.create_branch_agent(**validated_data)
            return agent

        except TypeError as e:
            raise serializers.ValidationError(
                {"errors": {"detail": e.args[0], "code": "invalid"}}
            )
