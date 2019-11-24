from django.core.mail import send_mail
from huey.contrib.djhuey import periodic_task, task


@task()
def send_async_email(
    subject=None, message=None, sender=None, recepients=[], fail_silently=True
):
    """
    Send emails asynchronously.
    """
    if not subject:
        raise TypeError("Subject cannot be empty")
    if not message:
        raise TypeError("Message cannot be empty")
    if not sender:
        raise TypeError("Sender cannot be empty")
    if not recepients:
        raise TypeError("Recipients cannot be empty")

    return send_mail(subject, message, sender, recepients)
