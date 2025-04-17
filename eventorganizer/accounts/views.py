


from django.shortcuts import render, redirect
from django.contrib.auth import login


from django.contrib.auth.forms import UserCreationForm

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            login(request, user)
            return redirect('home') 
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

