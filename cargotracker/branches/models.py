from django.db import models, IntegrityError
from django.contrib.auth import get_user_model
from django.conf import settings

from cargotracker.UTILS.tasks import send_async_email


class BranchManager(models.Manager):
    """
    This will have methods to easily help us interact with the Branch object. We override the default Django Manager.
    """

    def get_agent_branch(self, agent=None):
        """
        Get the agent's branch. If the agent does not have a branch, return None.
        """

        qs = Branch.objects.filter(branch_agent=agent)
        if qs.exists():
            return qs.first()
        return None

    def create_branch(self, city=None, main_branch=False, branch_agent=None):
        """
        This method helps us to create branches with their agents
        """

        if self.get_agent_branch(agent=branch_agent):
            raise TypeError("This agent already has an active branch assigned to them.")

        if not branch_agent:
            raise TypeError("Branches must have an agent.")

        if not isinstance(branch_agent, get_user_model()):
            raise TypeError("You must provide a valid User instance for all agents.")

        if not branch_agent or not branch_agent.is_staff:
            raise TypeError("All agents must be staff users.")
        if not city:
            raise TypeError("Branches must have a city")

        if main_branch and self.model.objects.filter(main_branch=True).exists():
            raise TypeError("There can only be one main branch.")

        try:
            branch = self.model.objects.create(
                city=city, main_branch=main_branch, branch_agent=branch_agent
            )
            subject = "Branch Assigned."
            message = f"Hello {branch_agent.username}, CargoTracker just opened a new branch in {city.title()} and you have been assigned as the branch manager there. You can log in and process all orders passing through your branch."
            send_async_email(
                subject=subject,
                message=message,
                sender=settings.ADMIN_EMAIL,
                recepients=[branch_agent.email,],
            )
            return branch

        except IntegrityError as e:
            raise TypeError("There already exists a branch in this city.") from e

    def search_by_city(self, city):
        """
        Return the branches found in a specific city.
        """
        if not city:
            raise TypeError("Provide a city for querying through.")
        return self.model.objects.get_queryset().filter(city__icontains=city)


class Branch(models.Model):
    """
    This represents a Branch where parcels are received and sent off to.
    """

    city = models.CharField(max_length=100, null=False, blank=False, unique=True)
    branch_agent = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="branch"
    )
    main_branch = models.BooleanField(default=False)

    objects = BranchManager()

    def __str__(self):
        """
        Return a human-readable representation
        """

        return f"{self.city}"
