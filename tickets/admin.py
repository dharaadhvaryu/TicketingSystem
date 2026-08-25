from django.contrib import admin
from .models import Ticket, TicketComment, TicketActivity
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        'ticket_number',
        'title',
        'company',
        'created_by',
        'assigned_to',
        'priority',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'priority',
        'company',
    )

    search_fields = (
        'ticket_number',
        'title',
        'description',
        'company__company_name',
    )

    readonly_fields = (
        'ticket_number',
        'created_at',
        'updated_at',
        'resolved_at',
        'closed_at',
    )

@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):

    list_display = (
        'ticket',
        'author',
        'comment_type',
        'created_at',
    )

    list_filter = (
        'comment_type',
        'created_at',
    )

    search_fields = (
        'message',
        'ticket__ticket_number',
        'author__username',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )# Register your models here.
@admin.register(TicketActivity)
class TicketActivityAdmin(admin.ModelAdmin):

    list_display = (
        'ticket',
        'activity_type',
        'user',
        'created_at',
    )

    list_filter = (
        'activity_type',
        'created_at',
    )

    search_fields = (
        'ticket__ticket_number',
        'description',
        'user__username',
    )

    readonly_fields = (
        'created_at',
    )