from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from apps.accounts.models import User
from .selectors import get_ticket_statistics


class TicketStatsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "tickets/ticket_stats.html"

    def test_func(self):
        return self.request.user.role in [User.Role.AGENT, User.Role.MANAGER]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_ticket_statistics())
        return context
    