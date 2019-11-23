from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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

        token['email'] = user.email

        return token

    def validate(self, attrs):
        """
        Override the validate method so we return payload bound to a `data` key.
        """

        data = super().validate(attrs)

        # return payload accessible through a `data` key
        return {"data": data}