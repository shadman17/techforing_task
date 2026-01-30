# Multi-Tenant Invitation System (Django + Docker)

This project demonstrates a **production-style multi-tenant backend** built with **Django**, focusing on:

- Multi-tenant invitation workflow
- Permission-aware endpoints (decorator-based)
- Asynchronous email sending with Celery
- Centralized structured logging (Grafana + Loki)
- Trace ID propagation across services
- Circuit breaker for outbound HTTP calls

The implementation is **intentionally simple**, but follows **real-world system-design patterns**.

---

## Architecture Overview

**Core stack**
- Django 5.x
- PostgreSQL
- Redis
- Celery + Celery Beat
- Docker & Docker Compose

**Observability**
- Grafana
- Loki
- Promtail

**Key Concepts Demonstrated**
- Multi-tenancy via request headers
- Permission decorator (Task 2)
- Centralized logging across multiple services (Task 3)
- Circuit breaker middleware for external services (Task 4)
- Trace ID propagation

---

## Prerequisites

Install on the host machine:

- Docker Desktop (with Docker Compose)
- Git

---

## Clone the Repository

```bash
git clone https://github.com/shadman17/techforing_task.git
```

## Environment Setup
This folder is used by Django and Promtail for log files.

```bash
mkdir logs
```

## Environment Setup
Create a .env file in the project root:
```bash
DEBUG=1
SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=tenant_db
POSTGRES_USER=tenant_user
POSTGRES_PASSWORD=tenant_pass
POSTGRES_HOST=db
POSTGRES_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=yourgmail@gmail.com
EMAIL_HOST_PASSWORD=YOUR_GMAIL_APP_PASSWORD
EMAIL_USE_TLS=1
DEFAULT_FROM_EMAIL=yourgmail@gmail.com

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

APP_BASE_URL=http://localhost:8000
```

## Start Core Services
```bash
docker compose up --build
```
Tenant service → http://localhost:8000, Auth service (second demo Django service) → http://localhost:8001, PostgreSQL, Redis, Celery worker, Celery beat

In a separate terminal
```bash
docker compose -f docker-compose.logging.yml up
```
This starts:

Grafana → http://localhost:3000, Loki, Promtail

## Initial Data Setup (Required)
Before using the APIs, seed minimal data.
Enter django shell in a terminal

```bash
docker compose exec web python manage.py shell
```

Create a Tenant
```bash
from invitations.models import Tenant
tenant = Tenant.objects.create(name="Acme Corp")
```

Seed Permission Rules (for dashboard access)
```bash
from permissions_app.models import PermissionRule

PermissionRule.objects.get_or_create(
    role="viewer",
    product_id="abc",
    feature="dashboard",
    permission="read",
)

PermissionRule.objects.get_or_create(
    role="admin",
    product_id="abc",
    feature="dashboard",
    permission="read",
)

```
Celery Beat DB Schedule

```bash
from django_celery_beat.models import CrontabSchedule, PeriodicTask

schedule, _ = CrontabSchedule.objects.get_or_create(
    minute="*/10",
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
```

exit shell
```bash
exit()
```

## API Usage
Common Headers
- X-Tenant-ID to Select tenant context
- X-Trace-ID for Distributed tracing
- Content-Type: application/json for JSON body

### Create Invitation
POST /api/invitations/
```bash
{
  "email": "user@example.com",
  "note": "Welcome to the platform"
}
```

### Accept Invitation
POST /api/invitations/accept
```bash
{
  "token": "<token-from-email>",
  "password": "StrongPass123"
}
```

### Cancel Invitation
POST /api/invitations/{invitation_id}/cancel/

### Dashboard (Permission Decorator)
GET /api/dashboard/

## Centralized Logging (Grafana)
Access Grafana
```bash
http://localhost:3000
```
username adn password: admin / admin

### Add Loki Data Source (one-time)
Grafana → Configuration → Data Sources → Add
Choose Loki
URL: http://loki:3100
Save & Test

### Explore Logs
Start with
```bash
{job="django"}
```

## Circuit Breaker
Outbound HTTP calls must use the provided wrapper:

```bash
from invitations.http_client import call_external_service
```