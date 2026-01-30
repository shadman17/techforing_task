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
docker compose build
docker compose up
docker compose -f docker-compose.logging.yml up