from django.urls import path
from .views import (
    DashboardAPIView,
    InvitationAcceptAPIView,
    InvitationCancelAPIView,
    InvitationCreateAPIView,
)


urlpatterns = [
    path("invitations/", InvitationCreateAPIView.as_view()),
    path("invitations/accept/", InvitationAcceptAPIView.as_view()),
    path("invitations/<int:invitation_id>/cancel/", InvitationCancelAPIView.as_view()),
    path("dashboard/", DashboardAPIView.as_view()),
]
