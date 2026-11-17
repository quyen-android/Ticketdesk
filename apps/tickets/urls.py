from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    path("stats/", views.TicketStatsView.as_view(), name="stats"),
]
