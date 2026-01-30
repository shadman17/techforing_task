# docker compose run --rm web python manage.py shell
# celery cron job
# Run Only Once!

from django_celery_beat.models import CrontabSchedule, PeriodicTask

schedule, _ = CrontabSchedule.objects.get_or_create(
    minute="*/60",
    hour="*",
    day_of_week="*",
    day_of_month="*",
    month_of_year="*",
)

PeriodicTask.objects.get_or_create(
    name="Expire pending invitations",
    crontab=schedule,
    task="invitations.tasks.expire_invitations",
)



# permission
from permissions_app.models import PermissionRule

PermissionRule.objects.get_or_create(role="admin", product_id="abc", feature="dashboard", permission="read")
PermissionRule.objects.get_or_create(role="admin", product_id="abc", feature="dashboard", permission="write")
PermissionRule.objects.get_or_create(role="viewer", product_id="abc", feature="dashboard", permission="read")

