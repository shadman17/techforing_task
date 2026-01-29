from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Invitation, Tenant, TenantMember


User = get_user_model()


class InvitationCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def create(self, validated_data):
        tenant = self.context["tenant"]
        ip = self.context.get("ip")
        email = validated_data["email"].lower()
        note = validated_data.get("note", "")
        name = email.split("@")[0]
        invite = Invitation.objects.create(
            tenant=tenant,
            name=name,
            email=email,
            status=Invitation.Status.PENDING,
            token=Invitation.generate_token(),
            expiration_date=Invitation.default_expiry(),
            invited_ip=ip,
            note=note,
        )
        return invite


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = [
            "id",
            "tenant",
            "name",
            "email",
            "status",
            "expiration_date",
            "created_at",
            "note",
        ]


class InvitationAcceptSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        try:
            invite = Invitation.objects.get(token=attrs["token"])
        except Invitation.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid token"})

        if invite.status != Invitation.Status.PENDING:
            raise serializers.ValidationError(
                {"token": f"Invitation is {invite.status}, not Pending"}
            )

        if timezone.now() >= invite.expiration_date:
            invite.status = Invitation.Status.EXPIRED
            invite.save(update_fields=["status", "updated_at"])
            raise serializers.ValidationError({"token": "Invitation expired"})

        attrs["invite"] = invite
        return attrs

    def save(self, **kwargs):
        invite = self.validated_data["invite"]
        password = self.validated_data["password"]

        user, created = User.objects.get_or_create(
            username=invite.email,
            defaults={"email": invite.email, "first_name": invite.name},
        )
        if created:
            user.set_password(password)
            user.save()
        else:
            pass

        TenantMember.objects.get_or_create(tenant=invite.tenant, user=user)

        invite.status = Invitation.Status.ACCEPTED
        invite.save(update_fields=["status", "updated_at"])
        return {"user_id": user.id, "tenant_id": invite.tenant_id}
