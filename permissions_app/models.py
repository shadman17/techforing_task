from django.db import models


class PermissionRule(models.Model):
    role = models.CharField(max_length=50)
    product_id = models.CharField(max_length=50)
    feature = models.CharField(max_length=50)
    permission = models.CharField(max_length=50)

    class Meta:
        unique_together = ("role", "product_id", "feature", "permission")

    def __str__(self):
        return f"{self.role} -> {self.product_id}.{self.feature}:{self.permission}"
