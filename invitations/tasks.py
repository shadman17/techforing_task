from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import Invitation


@shared_task
def send_invitation_email(
    invite_email: str, invite_name: str, tenant_name: str, token: str
):
    accept_url = f"{settings.APP_BASE_URL}/api/invitations/accept/"

    subject = f"Invitation to join {tenant_name}"
    message = (
        f"Hi {invite_name},\n\n"
        f"You have been invited to join tenant: {tenant_name}\n\n"
        f"To accept, call:\n"
        f"POST {accept_url}\n"
        f'Body: {{"token": "{token}", "password": "YOUR_PASSWORD"}}\n\n'
        f"This invite expires in 7 days.\n"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invite_email],
        fail_silently=False,
    )


@shared_task
def expire_invitations():
    now = timezone.now()
    qs = Invitation.objects.filter(
        status=Invitation.Status.PENDING,
        expiration_date__lte=now,
    )
    count = qs.update(status=Invitation.Status.EXPIRED)
    return f"Expired {count} invitations"
