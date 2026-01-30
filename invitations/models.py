from django.conf import settings
from django.db import models
import secrets
from datetime import timedelta
from django.utils import timezone


class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class TenantMember(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner"
        ADMIN = "admin"
        STAFF = "staff"
        VIEWER = "viewer"

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tenant_memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)

    class Meta:
        unique_together = ("tenant", "user")

    def __str__(self):
        return f"User ID: {self.user_id} -> Tenant ID: {self.tenant_id}"


class Invitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending"
        ACCEPTED = "Accepted"
        CANCELLED = "Cancelled"
        EXPIRED = "Expired"

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="invitations"
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    token = models.CharField(max_length=128, unique=True, db_index=True)
    expiration_date = models.DateTimeField()
    invited_ip = models.GenericIPAddressField(null=True, blank=True)
    note = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["email", "tenant"]),
            models.Index(fields=["status", "expiration_date"]),
        ]

    def __str__(self):
        return f"{self.email} ({self.tenant_id}) - {self.status}"

    @staticmethod
    def default_expiry():
        return timezone.now() + timedelta(days=7)

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expiration_date
