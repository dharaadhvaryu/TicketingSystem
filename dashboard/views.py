from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from tickets.models import Ticket
from tasks.models import Task

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from tickets.models import Ticket


@login_required
def dashboard(request):

    total_tickets = Ticket.objects.count()

    open_tickets = Ticket.objects.exclude(
        status__in=['RESOLVED', 'CLOSED']
    ).count()

    my_tickets = Ticket.objects.filter(
        assigned_to=request.user
    ).count()

    recent_tickets = Ticket.objects.order_by(
        '-created_at'
    )[:10]

    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'my_tickets': my_tickets,
        'my_tasks': 0,
        'recent_tickets': recent_tickets,
    }

    return render(
        request,
        'dashboard/dashboard.html',
        context
    )