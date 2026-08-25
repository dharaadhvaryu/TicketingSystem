from django.contrib import admin
from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'ticket',
        'title',
        'assigned_to',
        'priority',
        'status',
        'due_date',
        'created_at',
    )

    list_filter = (
        'status',
        'priority',
        'assigned_to',
    )

    search_fields = (
        'title',
        'description',
        'ticket__ticket_number',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'completed_at',
    )

# Register your models here.
