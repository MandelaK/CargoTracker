from rest_framework.serializers import ModelSerializer, ValidationError

from .models import Branch


class BranchSerializer(ModelSerializer):
    """
    Handle the logic for creating and updating branches
    """

    class Meta:
        model = Branch
        fields = "__all__"

    def create(self, validated_data):
        try:
            response = Branch.objects.create_branch(**validated_data)
            return response
        except TypeError as e:
            raise ValidationError(
                {"errors": {"detail": e.args[0], "code": "invalid"}}
            ) from e
