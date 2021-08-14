from django.contrib import auth
from django.contrib.messages.api import error
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
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
            if not form.is_valid():
                error_dict = form.errors.as_data()
                field_list = list(error_dict.values())
                for error_list in field_list:
                    for error in error_list:
                        #Send form errors as messages
                        messages.error(request, str(error)[2:-2])
                return redirect('register')
            else:
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account created for ' + user + '.' )
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
                messages.error(request, 'Username OR Password is incorrect.')
                return redirect('login')
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

@login_required(login_url='login')
def addFavourite(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except:
            return_info = {
                'success' : False,
                'result' : "ERROR input not in JSON format."
            }
            return JsonResponse(return_info)
        
        expected_keys = [ 'user', 'origin_name', 'origin_lat', 'origin_lon','destin_name', 'destin_lat', 'destin_lon', 'stops']

        #check if input is in correct format
        if list(data.keys()) != expected_keys:
            return_info = {
                'success' : False,
                'result' : "ERROR input keys are not correct."
            }
        #Check if Favourite with same user and co-ordinates exists
        elif favourite.objects.filter(user_id = data['user'], origin_lat = data['origin_lat'], origin_lon = data['origin_lon'], destin_lat = data['destin_lat'], destin_lon = data['destin_lon']).exists():
            return_info = {
                'success' : False,
                'result' : 'ERROR Duplicate favourite already exists.'
            }
        else:
            try:
                new_favourite = favourite(user_id = data['user'], origin_name= data['origin_name'], origin_lat = data['origin_lat'], origin_lon = data['origin_lon'], destin_name = data['destin_name'], destin_lat = data['destin_lat'], destin_lon = data['destin_lon'], stops = data['stops'])
                new_favourite.save()
                favourite_dict = model_to_dict(new_favourite)
                return_info = {
                    'success' : True,
                    'result' : "Favourite added.",
                    'favourite' : favourite_dict
                }
                return JsonResponse(return_info)
            except:
                return_info = {
                    'success' : False,
                    'result' : "ERROR unable to save new favourite."
                }
                return JsonResponse(return_info)
        
        return JsonResponse(return_info)
    else:
        return redirect('index')

@login_required(login_url='login')
def removeFavourite(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            favourite.objects.get(pk=data['id']).delete()
            return_info = { 
                'success': True, 
                'result' : "Favourite dropped."
            }
        except:
            return_info = { 
                'success': False,
                'result' : "ERROR could not delete."
            }
        return JsonResponse(return_info)
    else:
        return redirect('index')

@login_required(login_url='login')
def renameFavourite(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            renamed_favourite = favourite.objects.get(pk=data['id'])
            renamed_favourite.favourite_name = data['new_name']
            renamed_favourite.save(update_fields=['favourite_name'])
            return_info = {
                'success' : True,
                'result' : "Rename successful.",
                'name' : renamed_favourite.favourite_name
            }
            return JsonResponse(return_info)
        except:
            return_info = {
                'success' : False,
                'result' : "ERROR could not rename."
            }
            return JsonResponse(return_info)
    else:
        return redirect('index')
