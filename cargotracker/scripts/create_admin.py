"""This script is called to create an admin user."""

from authentication.models import User, IntegrityError


def run(*args):
    """
    Create admin using this command. If the email already is registered, just return the email and no need to create new users.
    """

    if args and "email" in args[0]:
        email = args[0].split("=")[1]
        admin = User.objects.get_user(email=email)
        if admin:
            print(f"Admin already exists with this email: {admin.email}")
            return
        admin = User.objects.create_superuser(
            email=email, password="adminpassword", username=email
        )
        if admin:
            print(f"New admin user created with email: {admin.email}")
            return
        return False

    print("Please provide email and try again")
    return
