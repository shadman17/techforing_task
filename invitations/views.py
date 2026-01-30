from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions_app.decorators import check_permission
from invitations.http_client import call_external_service

from .models import Invitation, Tenant
from .serializers import (
    InvitationAcceptSerializer,
    InvitationCreateSerializer,
    InvitationSerializer,
)
from .tasks import send_invitation_email


import logging

logger = logging.getLogger(__name__)


class InvitationCreateAPIView(APIView):
    def post(self, request):
        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            return Response(
                {"detail": "X-Tenant-ID header missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return Response(
                {"detail": "Invalid tenant"}, status=status.HTTP_400_BAD_REQUEST
            )

        ip = request.META.get("REMOTE_ADDR")
        serializer = InvitationCreateSerializer(
            data=request.data, context={"tenant": tenant, "ip": ip}
        )
        serializer.is_valid(raise_exception=True)
        invite = serializer.save()

        send_invitation_email.delay(
            invite.email, invite.name, invite.tenant.name, invite.token
        )

        logger.info(
            "Invitation created",
            extra={
                "trace_id": request.trace_id,
                "user_id": request.user.id if request.user.is_authenticated else None,
                "tenant_id": tenant.id,
            },
        )

        return Response(
            InvitationSerializer(invite).data, status=status.HTTP_201_CREATED
        )


class InvitationAcceptAPIView(APIView):
    """
    POST /api/invitations/accept/
    Body: { token, password }
    """

    def post(self, request):
        serializer = InvitationAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        logger.info(
            "Invitation accepted",
            extra={
                "trace_id": request.trace_id,
                "user_id": request.user.id,
                "tenant_id": request.invite.tenant_id,
            },
        )

        return Response(
            {"detail": "Invitation accepted", **result}, status=status.HTTP_200_OK
        )


class InvitationCancelAPIView(APIView):
    """
    POST /api/invitations/<id>/cancel/
    """

    def post(self, request, invitation_id: int):
        try:
            invite = Invitation.objects.get(id=invitation_id)
        except Invitation.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if invite.status != Invitation.Status.PENDING:
            return Response(
                {"detail": f"Cannot cancel. Status is {invite.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invite.status = Invitation.Status.CANCELLED
        invite.save(update_fields=["status", "updated_at"])

        logger.info(
            "Invitation cancelled",
            extra={
                "trace_id": request.trace_id,
                "user_id": request.user.id if request.user.is_authenticated else None,
                "tenant_id": invite.tenant_id,
            },
        )

        return Response({"detail": "Invitation cancelled"}, status=status.HTTP_200_OK)


class DashboardAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    @check_permission(product_id="abc", feature="dashboard", permission="read")
    def get(self, request):
        logger.info(
            "Dashboard accessed",
            extra={
                "trace_id": request.trace_id,
                "user_id": None,
                "tenant_id": request.tenant_id,
            },
        )

        return Response(
            {
                "tenant_id": request.tenant_id,
                "role": request.role,
                "message": "Dashboard data",
            }
        )
