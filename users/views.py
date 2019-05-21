from django.shortcuts import render
from django.shortcuts import redirect
from .admin import UserCreationForm, UserChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def create_new_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, (f"User created for {form.cleaned_data.get('email')},"
                          "please log in to continue"))
            return redirect('login')

    else:
        form = UserCreationForm()
    return render(request, 'users/new_user.html', {'form': form})


@login_required
def edit_user(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'changes were saved')
            return redirect('profile')
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})
