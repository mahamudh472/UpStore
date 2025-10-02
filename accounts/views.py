from django.shortcuts import render, redirect
from django.contrib import messages ## For message
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, date
from .models import UserProfile
from store.models import Cart

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
                return redirect("accounts:login")
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
                    return redirect("accounts:login")
                
            except:
                return redirect("accounts:login")
    return render(request, 'account/login.html')

def logout_view(request):
    logout(request)
    return redirect("/")

@login_required
def profile_view(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == "POST":
        try:
            # Get form data
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            email = request.POST.get("email", "").strip()
            bio = request.POST.get("bio", "").strip()
            address = request.POST.get("address", "").strip()
            phone_number = request.POST.get("phone_number", "").strip()
            date_of_birth = request.POST.get("date_of_birth", "").strip()
            gender = request.POST.get("gender", "").strip()
            
            # Validate email format
            if email:
                import re
                email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                if not re.match(email_pattern, email):
                    messages.error(request, "Please enter a valid email address.")
                    return redirect("accounts:profile")
            
            # Validate email uniqueness (excluding current user)
            if email and User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.error(request, "This email is already in use by another account.")
                return redirect("accounts:profile")
            
            # Validate and process date of birth
            processed_date_of_birth = None
            if date_of_birth:
                try:
                    # Parse the date
                    processed_date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                    
                    # Check if date is not in the future
                    if processed_date_of_birth > datetime.now().date():
                        messages.error(request, "Date of birth cannot be in the future.")
                        return redirect("accounts:profile")
                        
                except ValueError:
                    messages.error(request, "Please enter a valid date of birth.")
                    return redirect("accounts:profile")
            
            # Validate phone number (basic validation)
            if phone_number and len(phone_number.replace(' ', '').replace('-', '').replace('+', '')) < 10:
                messages.error(request, "Please enter a valid phone number.")
                return redirect("accounts:profile")
            
            # Update User model
            if first_name:
                request.user.first_name = first_name
            if last_name:
                request.user.last_name = last_name
            if email:
                request.user.email = email
            
            # Save user with validation
            try:
                request.user.full_clean()  # This will validate the model
                request.user.save()
            except ValidationError as ve:
                if 'email' in ve.message_dict:
                    messages.error(request, "Please enter a valid email address.")
                else:
                    messages.error(request, "Please check your user information.")
                return redirect("accounts:profile")
            
            # Update UserProfile model
            user_profile.bio = bio
            user_profile.address = address
            user_profile.phone_number = phone_number
            user_profile.date_of_birth = processed_date_of_birth
            user_profile.gender = gender if gender else None
            
            # Handle profile image upload
            if 'profile_image' in request.FILES:
                uploaded_file = request.FILES['profile_image']
                
                # Validate file size (5MB limit)
                if uploaded_file.size > 5 * 1024 * 1024:
                    messages.error(request, "Profile image must be smaller than 5MB.")
                    return redirect("accounts:profile")
                
                # Validate file type
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
                if uploaded_file.content_type not in allowed_types:
                    messages.error(request, "Profile image must be in JPEG, PNG, or GIF format.")
                    return redirect("accounts:profile")
                
                user_profile.image = uploaded_file
            
            # Save profile with validation
            try:
                user_profile.full_clean()  # This will validate the model
                user_profile.save()
            except ValidationError as ve:
                messages.error(request, f"Profile validation error: {ve}")
                return redirect("accounts:profile")
            
            messages.success(request, "Profile updated successfully!")
            
        except IntegrityError as e:
            messages.error(request, "There was an error updating your profile. This might be due to duplicate data. Please try again.")
            print(f"IntegrityError in profile update: {str(e)}")  # For debugging
        except ValidationError as e:
            messages.error(request, f"Validation error: {str(e)}")
            print(f"ValidationError in profile update: {str(e)}")  # For debugging
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            print(f"Unexpected error in profile update: {str(e)}")  # For debugging
        
        return redirect("accounts:profile")
    
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'cart_items': Cart.objects.filter(user=request.user).count(),
        'total_orders': 0,  # You can implement this later with an Order model
        'wishlist_count': 0,  # You can implement this later with a Wishlist model
        'today': date.today(),  # For date validation in template
    }
    return render(request, 'account/profile.html', context)
