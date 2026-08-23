from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


def login_view(request):

    role = request.GET.get("role", "student")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Faculty login
            if role == "faculty":
                return redirect("faculty_dashboard")

            # Student login
            return redirect("student_dashboard")

        return render(
            request,
            "accounts/login.html",
            {
                "error": "Invalid username or password.",
                "role": role,
            }
        )

    return render(
        request,
        "accounts/login.html",
        {
            "role": role,
        }
    )


from django.shortcuts import render


def landing_page(request):
    return render(request, 'home/landing.html')