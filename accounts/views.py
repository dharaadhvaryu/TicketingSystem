from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


def login_view(request):

    if request.user.is_authenticated:
        return redirect('ticket_list')

    error = None

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            next_page = request.GET.get(
                'next'
            )

            if next_page:
                return redirect(next_page)

            return redirect(
                'ticket_list'
            )

        else:

            error = (
                'Invalid username or password.'
            )

    return render(
        request,
        'accounts/login.html',
        {
            'error': error
        }
    )


def logout_view(request):

    logout(request)

    return redirect('login')

# Create your views here.
