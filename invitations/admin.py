from django.contrib import admin
from .models import Invitation, Tenant, TenantMember

# Register your models here.
admin.site.register(Invitation)
admin.site.register(Tenant)
admin.site.register(TenantMember)
