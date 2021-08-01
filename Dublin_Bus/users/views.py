from django.contrib import auth
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from Bus.models import Stop
from .models import favourite
import json

from .forms import CreateUserForm

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        form = CreateUserForm()

        #New user Registered
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account created for ' + user )
                return redirect('login')
        
        context = {'form': form}
        return render(request, 'users/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username= username, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.info(request, 'Username OR Password is incorrect')
        return render(request, 'users/login.html')

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def favourites(request):
    current_user = request.user
    favourites = favourite.objects.filter(user_id=current_user.id)
    context = {'favourites': favourites}
    return render(request, 'users/favourites.html', context)


def makeFavourite(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_favourite = favourite(user_id = data['user'], origin_name= data['origin_name'], origin_lat = data['origin_lat'], origin_lon = data['origin_lon'], destin_name = data['destin_name'], destin_lat = data['destin_lat'], destin_lon = data['destin_lon'], stops = data['stops'])
        new_favourite.save()
        return JsonResponse(data)
    else:
        return redirect('index')



#def test(request):
#    stop1 = Stop.objects.get(stop_id='8220DB000004')
#    stop2 = Stop.objects.get(stop_id='8220DB000045')
#    current_user = request.user
#    k = favourite(user_id = 3, origin_name= stop1.stop_name, origin_lat = stop1.stop_lat, origin_lon = stop1.stop_lon, destin_name = stop2.stop_name, destin_lat = stop2.stop_lat, destin_lon = stop2.stop_lon)
#    k.save()
#    return redirect('index')
