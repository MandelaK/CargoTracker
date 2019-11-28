from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as APIValidationError
from django.contrib.auth import get_user_model

from branches.models import Branch

User = get_user_model()


def validate_that_email_belongs_to_active_agent(email):
    """
    Validate that a passed email belongs to an active agent. Raise a DRF Validation Error if any errors are encountered.
    """
    validate_email = EmailValidator()
    try:
        validate_email(email)
        agent = User.objects.get(email=email)
        if agent.is_staff:
            return (agent.email, agent)
        raise User.DoesNotExist
    except ValidationError as e:
        raise APIValidationError({"detail": e.args[0], "code": "ivalid"}) from e
    except User.DoesNotExist as e:
        raise APIValidationError(
            {"detail": "There is no agent registered with the provided email address."}
        ) from e


def validate_branch_exists_in_city(city):
    """
    Validate whether a branch indeed exists in the provided city.
    """

    branch = Branch.objects.search_by_city_exact(city)
    return branch if branch else False
