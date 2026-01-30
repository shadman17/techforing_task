from functools import wraps
from rest_framework.response import Response
from rest_framework import status

from invitations.models import TenantMember
from permissions_app.models import PermissionRule


def check_permission(product_id: str, feature: str, permission: str):
    def decorator(view_method):
        @wraps(view_method)
        def _wrapped(self, request, *args, **kwargs):
            tenant_id = request.headers.get("X-Tenant-ID")
            if not tenant_id:
                return Response(
                    {"detail": "X-Tenant-ID header missing"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if request.user.is_authenticated:
                try:
                    membership = TenantMember.objects.get(
                        tenant_id=tenant_id,
                        user=request.user,
                    )
                    role = membership.role
                except TenantMember.DoesNotExist:
                    return Response(
                        {"detail": "User not part of this tenant"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                user_id = request.user.id
            else:
                role = "viewer"
                user_id = None

            allowed = PermissionRule.objects.filter(
                role=role,
                product_id=product_id,
                feature=feature,
                permission=permission,
            ).exists()

            if not allowed:
                return Response(
                    {"detail": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # attach context for downstream use & logging
            request.tenant_id = int(tenant_id)
            request.role = role

            return view_method(self, request, *args, **kwargs)

        return _wrapped

    return decorator
