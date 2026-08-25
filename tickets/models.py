from django.db import models
from django.db import models
from django.contrib.auth.models import User
from companies.models import Company


class Ticket(models.Model):

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('WAITING', 'Waiting for Client'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
        ('REOPENED', 'Reopened'),
    ]

    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tickets'
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )

    title = models.CharField(
        max_length=250
    )

    description = models.TextField()

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    due_date = models.DateTimeField(
        null=True,
        blank=True
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):

        if not self.ticket_number:

            last_ticket = Ticket.objects.order_by(
                '-id'
            ).first()

            if last_ticket:
                next_number = last_ticket.id + 1
            else:
                next_number = 1001

            self.ticket_number = f"T-{next_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number} - {self.title}"

		
class TicketComment(models.Model):

    COMMENT_TYPE_CHOICES = [
        ('PUBLIC', 'Public Reply'),
        ('INTERNAL', 'Internal Note'),
    ]

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    comment_type = models.CharField(
        max_length=10,
        choices=COMMENT_TYPE_CHOICES,
        default='PUBLIC'
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.ticket.ticket_number} - "
            f"{self.author.username if self.author else 'Unknown'}"
        )
		# Create your models here.
class TicketActivity(models.Model):

    ACTIVITY_TYPE_CHOICES = [
        ('CREATED', 'Ticket Created'),
        ('ASSIGNED', 'Ticket Assigned'),
        ('STATUS', 'Status Changed'),
        ('PRIORITY', 'Priority Changed'),
        ('COMMENT', 'Comment Added'),
        ('TASK', 'Task Created'),
        ('UPDATED', 'Ticket Updated'),
        ('RESOLVED', 'Ticket Resolved'),
        ('CLOSED', 'Ticket Closed'),
    ]

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='activities'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.ticket.ticket_number} - "
            f"{self.activity_type}"
        )