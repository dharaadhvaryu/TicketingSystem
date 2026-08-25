from .models import TicketActivity
from django.core.mail import send_mail
from django.conf import settings

def create_activity(
    ticket,
    user,
    activity_type,
    description
):
    return TicketActivity.objects.create(
        ticket=ticket,
        user=user,
        activity_type=activity_type,
        description=description
    )
	



def send_ticket_notification(
    ticket,
    subject,
    message,
    include_creator=True,
    include_assigned=True
):
    recipients = []

    # Ticket creator
    if (
        include_creator
        and ticket.created_by
        and ticket.created_by.email
    ):
        recipients.append(ticket.created_by.email)

    # Assigned staff
    if (
        include_assigned
        and ticket.assigned_to
        and ticket.assigned_to.email
    ):
        recipients.append(ticket.assigned_to.email)

    # Remove duplicates
    recipients = list(dict.fromkeys(recipients))

    if not recipients:
        return

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=False
    )