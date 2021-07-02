from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

# Create your views here.
from .forms import LoginForm, RegisterForm, User


def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        password2 = form.cleaned_data.get("password2")

        # noinspection PyBroadException
        try:
            user = User.objects.create_user(username, email, password)
        except:
            user = None

        if user is not None:
            # user is valid and active -> is active
            # request.user == user
            login(request, user)
            return redirect("/")
        else:
            request.session['registration_error'] = 1  # 1 == True
    return render(request, "forms.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        # check if this is a user and their password is valid
        user = authenticate(request, username=username, password=password)
        if user != None:
            # user is valid and active -> is active
            # request.user == user
            login(request, user)
            return redirect("/")
        else:
            # verify if user has attempted too many times
            # attempt = request.session.get("attempt") or 0
            # request.session['attempt'] = attempt + 1
            # return redirect("/invalid-password")
            request.session['invalid_user'] = 1  # 1 == True
    return render(request, "forms.html", {"form": form})


def logout_view(request):
    logout(request)
    # request.user == Anon User
    return redirect("/login")
