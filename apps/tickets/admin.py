from django.contrib import admin
from apps.tickets.models import Category, Comment, Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "status", "priority", "assignee", "created_at"]
    list_filter = ["status", "priority", "category"]
    search_fields = ["title", "description"]
    autocomplete_fields = ["assignee"]


admin.site.register(Category)
admin.site.register(Comment)