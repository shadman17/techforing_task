from functools import wraps

from rest_framework.response import Response
from rest_framework import status

from invitations.models import TenantMember
from permissions_app.models import PermissionRule


def check_permission(product_id: str, feature: str, permission: str):
    """
    Simple decorator for DRF APIViews.
    Expects:
      - Authenticated user (request.user)
      - Tenant ID from header: X-Tenant-ID
    """

    def decorator(view_method):
        @wraps(view_method)
        def _wrapped(self, request, *args, **kwargs):
            user = request.user
            if not user or not user.is_authenticated:
                return Response(
                    {"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
                )

            tenant_id = request.headers.get("X-Tenant-ID")
            if not tenant_id:
                return Response(
                    {"detail": "X-Tenant-ID header missing"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                membership = TenantMember.objects.get(tenant_id=tenant_id, user=user)
            except TenantMember.DoesNotExist:
                return Response(
                    {"detail": "User not part of this tenant"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            role = membership.role

            allowed = PermissionRule.objects.filter(
                role=role,
                product_id=product_id,
                feature=feature,
                permission=permission,
            ).exists()

            if not allowed:
                return Response(
                    {"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
                )

            # optionally attach for downstream usage
            request.tenant_id = int(tenant_id)
            request.role = role

            return view_method(self, request, *args, **kwargs)

        return _wrapped

    return decorator
