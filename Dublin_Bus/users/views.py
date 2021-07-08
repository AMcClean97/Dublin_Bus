from django.shortcuts import redirect, render
#from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import CreateUserForm

# Create your views here.
def registerPage(request):
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
    context = {}
    return render(request, 'users/login.html', context)


