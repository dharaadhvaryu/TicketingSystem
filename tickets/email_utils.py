from django.core.mail import send_mail
from django.conf import settings


def send_ticket_notification(
    ticket,
    subject,
    message,
    include_creator=True,
    include_assigned=True
):
    """
    Send an email notification related to a ticket.

    Creator and assigned staff are included when they have
    an email address.
    """

    recipients = []

    # ------------------------------------------
    # TICKET CREATOR
    # ------------------------------------------

    if include_creator:

        if (
            ticket.created_by
            and ticket.created_by.email
        ):
            recipients.append(
                ticket.created_by.email
            )

    # ------------------------------------------
    # ASSIGNED STAFF
    # ------------------------------------------

    if include_assigned:

        if (
            ticket.assigned_to
            and ticket.assigned_to.email
        ):
            recipients.append(
                ticket.assigned_to.email
            )

    # ------------------------------------------
    # REMOVE DUPLICATE EMAILS
    # ------------------------------------------

    recipients = list(
        dict.fromkeys(recipients)
    )

    # ------------------------------------------
    # SEND EMAIL
    # ------------------------------------------

    if recipients:

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False
        )
"""@login_required
def test_email(request):

    send_mail(
        'Service Desk Test Email',
        'This is a test email from your Django Service Desk.',
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        fail_silently=False
    )

    return HttpResponse(
        'Test email sent successfully.'
    )"""