from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User

from .models import Ticket, TicketComment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Ticket, TicketComment, TicketActivity
from .email_utils import send_ticket_notification
from companies.models import Company
from .utils import create_activity
from .forms import TicketForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from .models import Ticket
from companies.models import Company
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings



@login_required
def ticket_list(request):

    # -----------------------------
    # GET FILTER VALUES
    # -----------------------------

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    priority = request.GET.get("priority", "").strip()
    company_id = request.GET.get("company", "").strip()
    assigned_to_id = request.GET.get("assigned_to", "").strip()


    # -----------------------------
    # BASE QUERY
    # -----------------------------

    tickets = Ticket.objects.select_related(
        "company",
        "created_by",
        "assigned_to"
    ).order_by("-created_at")


    # -----------------------------
    # SEARCH
    # -----------------------------

    if search:

        tickets = tickets.filter(
            Q(ticket_number__icontains=search)
            |
            Q(title__icontains=search)
            |
            Q(description__icontains=search)
            |
            Q(company__company_name__icontains=search)
        )


    # -----------------------------
    # STATUS
    # -----------------------------

    if status:

        tickets = tickets.filter(
            status=status
        )


    # -----------------------------
    # PRIORITY
    # -----------------------------

    if priority:

        tickets = tickets.filter(
            priority=priority
        )


    # -----------------------------
    # COMPANY
    # -----------------------------

    if company_id:

        tickets = tickets.filter(
            company_id=company_id
        )


    # -----------------------------
    # ASSIGNED STAFF
    # -----------------------------

    if assigned_to_id:

        tickets = tickets.filter(
            assigned_to_id=assigned_to_id
        )


    # -----------------------------
    # DROPDOWN DATA
    # -----------------------------

    companies = Company.objects.order_by(
        "company_name"
    )

    staff_users = User.objects.filter(
        is_active=True
    ).order_by(
        "username"
    )


    context = {

        "tickets": tickets,

        "companies": companies,

        "staff_users": staff_users,

        "search": search,

        "selected_status": status,

        "selected_priority": priority,

        "selected_company": company_id,

        "selected_assigned_to": assigned_to_id,

    }


    return render(
        request,
        "tickets/ticket_list.html",
        context
    )

@login_required
def ticket_detail(request, ticket_id):

    ticket = get_object_or_404(
        Ticket.objects.select_related(
            'company',
            'created_by',
            'assigned_to'
        ),
        id=ticket_id
    )

    # ==================================================
    # HANDLE FORM SUBMISSIONS
    # ==================================================

    if request.method == 'POST':

        action = request.POST.get('action')

        # ==================================================
        # ADD COMMENT
        # ==================================================

        if action == 'comment':

            message = request.POST.get(
                'message',
                ''
            ).strip()

            comment_type = request.POST.get(
                'comment_type',
                'PUBLIC'
            )

            if message:

                TicketComment.objects.create(
                    ticket=ticket,
                    author=request.user,
                    comment_type=comment_type,
                    message=message
                )

                # Activity history
                if comment_type == 'INTERNAL':

                    description = (
                        f"{request.user.username} "
                        f"added an internal note."
                    )

                else:

                    description = (
                        f"{request.user.username} "
                        f"added a public reply."
                    )

                create_activity(
                    ticket=ticket,
                    user=request.user,
                    activity_type='COMMENT',
                    description=description
                )

                # ------------------------------------------
                # EMAIL ONLY FOR PUBLIC COMMENTS
                # ------------------------------------------

                if comment_type == 'PUBLIC':

                    subject = (
                        f"Ticket {ticket.ticket_number} "
                        f"- New Reply"
                    )

                    email_message = f"""
Hello,

A new public reply has been added to your support ticket.

Ticket: {ticket.ticket_number}
Title: {ticket.title}

Updated by: {request.user.username}

Message:

{message}

Please log in to the Service Desk to view the complete conversation.

Regards,
Service Desk
"""

                    send_ticket_notification(
                        ticket=ticket,
                        subject=subject,
                        message=email_message,
                        include_creator=True,
                        include_assigned=True
                    )

            return redirect(
                'ticket_detail',
                ticket_id=ticket.id
            )

        # ==================================================
        # UPDATE TICKET
        # ==================================================

        elif action == 'update_ticket':

            old_status = ticket.status
            old_priority = ticket.priority
            old_assigned = ticket.assigned_to

            new_status = request.POST.get(
                'status'
            )

            new_priority = request.POST.get(
                'priority'
            )

            assigned_to_id = request.POST.get(
                'assigned_to'
            )

            # ------------------------------------------
            # Track changes for ONE email
            # ------------------------------------------

            changes = []

            # ==================================================
            # STATUS
            # ==================================================

            if (
                new_status
                and new_status != old_status
            ):

                ticket.status = new_status

                old_status_label = dict(
                    Ticket.STATUS_CHOICES
                ).get(
                    old_status,
                    old_status
                )

                new_status_label = dict(
                    Ticket.STATUS_CHOICES
                ).get(
                    new_status,
                    new_status
                )

                changes.append(
                    f"Status: {old_status_label} → "
                    f"{new_status_label}"
                )

                create_activity(
                    ticket=ticket,
                    user=request.user,
                    activity_type='STATUS',
                    description=(
                        f"Status changed from "
                        f"{old_status_label} to "
                        f"{new_status_label}."
                    )
                )

                # Resolved timestamp
                if (
                    new_status == 'RESOLVED'
                    and old_status != 'RESOLVED'
                ):
                    ticket.resolved_at = timezone.now()

                # Closed timestamp
                if (
                    new_status == 'CLOSED'
                    and old_status != 'CLOSED'
                ):
                    ticket.closed_at = timezone.now()

            # ==================================================
            # PRIORITY
            # ==================================================

            if (
                new_priority
                and new_priority != old_priority
            ):

                ticket.priority = new_priority

                old_priority_label = dict(
                    Ticket.PRIORITY_CHOICES
                ).get(
                    old_priority,
                    old_priority
                )

                new_priority_label = dict(
                    Ticket.PRIORITY_CHOICES
                ).get(
                    new_priority,
                    new_priority
                )

                changes.append(
                    f"Priority: {old_priority_label} → "
                    f"{new_priority_label}"
                )

                create_activity(
                    ticket=ticket,
                    user=request.user,
                    activity_type='PRIORITY',
                    description=(
                        f"Priority changed from "
                        f"{old_priority_label} to "
                        f"{new_priority_label}."
                    )
                )

            # ==================================================
            # ASSIGNMENT
            # ==================================================

            new_assigned = None

            if assigned_to_id:

                new_assigned = get_object_or_404(
                    User,
                    id=assigned_to_id
                )

                old_name = (
                    old_assigned.username
                    if old_assigned
                    else 'Unassigned'
                )

                new_name = new_assigned.username

                if (
                    old_assigned is None
                    or old_assigned.id != new_assigned.id
                ):

                    ticket.assigned_to = new_assigned

                    changes.append(
                        f"Assigned To: {old_name} → "
                        f"{new_name}"
                    )

                    create_activity(
                        ticket=ticket,
                        user=request.user,
                        activity_type='ASSIGNED',
                        description=(
                            f"Ticket assigned from "
                            f"{old_name} to "
                            f"{new_name}."
                        )
                    )

            else:

                if old_assigned is not None:

                    ticket.assigned_to = None

                    changes.append(
                        f"Assigned To: "
                        f"{old_assigned.username} → "
                        f"Unassigned"
                    )

                    create_activity(
                        ticket=ticket,
                        user=request.user,
                        activity_type='ASSIGNED',
                        description=(
                            f"Ticket unassigned from "
                            f"{old_assigned.username}."
                        )
                    )

            # ==================================================
            # SAVE TICKET
            # ==================================================

            ticket.save()

            # ==================================================
            # SEND ONE EMAIL FOR ALL CHANGES
            # ==================================================

            if changes:

                subject = (
                    f"Ticket {ticket.ticket_number} "
                    f"- Updated"
                )

                change_text = "\n".join(
                    f"- {change}"
                    for change in changes
                )

                email_message = f"""
Hello,

Your support ticket has been updated.

Ticket: {ticket.ticket_number}
Title: {ticket.title}

Changes made:

{change_text}

Updated by: {request.user.username}

Current Status:
{ticket.get_status_display()}

Current Priority:
{ticket.get_priority_display()}

Please log in to the Service Desk to view the complete ticket.

Regards,
Service Desk
"""

                send_ticket_notification(
                    ticket=ticket,
                    subject=subject,
                    message=email_message,
                    include_creator=True,
                    include_assigned=True
                )

            return redirect(
                'ticket_detail',
                ticket_id=ticket.id
            )

    # ==================================================
    # PAGE DATA
    # ==================================================

    tasks = ticket.tasks.select_related(
        'assigned_to'
    ).order_by('created_at')

    comments = ticket.comments.select_related(
        'author'
    ).order_by('created_at')

    activities = ticket.activities.select_related(
        'user'
    ).order_by('-created_at')

    users = User.objects.filter(
        is_active=True
    ).order_by('username')

    context = {
        'ticket': ticket,
        'tasks': tasks,
        'comments': comments,
        'activities': activities,
        'users': users,
        'status_choices': Ticket.STATUS_CHOICES,
        'priority_choices': Ticket.PRIORITY_CHOICES,
    }

    return render(
        request,
        'tickets/ticket_detail.html',
        context
    )
@login_required
def ticket_create(request):

    if request.method == 'POST':

        form = TicketForm(request.POST)

        if form.is_valid():

            ticket = form.save(
                commit=False
            )

            ticket.created_by = request.user

            ticket.save()

            create_activity(
                ticket=ticket,
                user=request.user,
                activity_type='CREATED',
                description=(
                    f"Ticket {ticket.ticket_number} "
                    f"was created."
                )
            )

            return redirect(
                'ticket_detail',
                ticket_id=ticket.id
            )

    else:

        form = TicketForm()

    return render(
        request,
        'tickets/ticket_create.html',
        {
            'form': form
        }
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