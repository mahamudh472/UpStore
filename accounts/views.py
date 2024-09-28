from django.shortcuts import render, redirect
from django.contrib import messages ## For message
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .models import UserProfile

def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        address = request.POST.get("address")
        gender = request.POST.get("gender")
        date_of_birth = request.POST.get("date-of-birth")
        full_name = request.POST.get("full-name")

        # check email address
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("account:register")
        
        # Check password validity
        if password != password2:
            messages.error(request, "Password and confirm password didn't match!")
            return redirect("account:register")
        first_name, last_name = full_name.split()[0], "".join(full_name.split()[1:]) if len(full_name.split())>1 else ""
        username = email.split("@")[0]
        u = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name, username=username)
        u.save()
        user = authenticate(username=username, password=password)
        print(user)
        if user:
            user_profile = UserProfile.objects.create(
                user = user,
                address = address,
                gender = gender,
                date_of_birth = date_of_birth,
            )
            user_profile.save()
        login(request, user)
        print("success")
        return redirect("/")
    return render(request, 'account/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username, password)
        if User.objects.filter(username=username).exists():
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                print("Success")
                return redirect("/")
            else:
                messages.error(request, "Authentication failed")
                return redirect("account:login")
        else:
            try:
                us = User.objects.get(email=username).username
                user = authenticate(username=us, password=password)
                if user:
                    login(request, user)
                    print("success")
                    return redirect("/")
                else:
                    print("Not a user")
                    return redirect("account:login")
                
            except:
                return redirect("account:login")
    return render(request, 'account/login.html')

def logout_view(request):
    logout(request)
    return redirect("/")
