from django.db.models import Count, Q
from apps.accounts.models import User
from apps.tickets.models import Ticket


def get_ticket_statistics() -> dict:
    summary = Ticket.objects.aggregate(
        total=Count("id"),
        unassigned=Count("id", filter=Q(assignee__isnull=True)),
        high_priority=Count("id", filter=Q(priority=Ticket.Priority.HIGH)),
        resolved_or_closed=Count(
            "id",
            filter=Q(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]),
        ),
    )

    raw_by_status = (
        Ticket.objects.values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )
    status_labels = dict(Ticket.Status.choices)
    by_status = [
        {
            "status": row["status"],
            "label": status_labels.get(row["status"], row["status"]),
            "total": row["total"],
        }
        for row in raw_by_status
    ]

    by_assignee_qs = (
        User.objects.filter(role__in=[User.Role.AGENT, User.Role.MANAGER])
        .annotate(
            total_assigned=Count("assigned_tickets"),
            open_count=Count(
                "assigned_tickets",
                filter=~Q(assigned_tickets__status=Ticket.Status.CLOSED),
            ),
            closed_count=Count(
                "assigned_tickets",
                filter=Q(assigned_tickets__status=Ticket.Status.CLOSED),
            ),
        )
        .order_by("-open_count", "username")
    )

    # Chart
    status_chart_data = {
        "labels": [item["label"] for item in by_status],
        "data": [item["total"] for item in by_status],
    }

    assignee_chart_data = {
        "labels": [u.username for u in by_assignee_qs],
        "open_data": [u.open_count for u in by_assignee_qs],
        "closed_data": [u.closed_count for u in by_assignee_qs],
    }

    urgent_tickets = (
        Ticket.objects.select_related("category", "created_by", "assignee")
        .filter(priority=Ticket.Priority.HIGH)
        .exclude(status=Ticket.Status.CLOSED)
        .order_by("-created_at")[:8]
    )

    return {
        "summary": summary,
        "by_status": by_status,
        "by_assignee": by_assignee_qs,
        "status_chart_data": status_chart_data,
        "assignee_chart_data": assignee_chart_data,
        "urgent_tickets": urgent_tickets,
    }
