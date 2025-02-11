from django.shortcuts import render, redirect
from .models import Albumin, CustomUser, Profile
from .forms import AlbuminForm
from django.contrib.auth.models import User
from django.conf import settings
from django.apps import apps
from django.contrib.auth.decorators import login_required
import json
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
import base64
import uuid
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.db import IntegrityError


def Home(request):
    return render(request, "home.html")

# def search_category(request):
#     category = request.GET.get('category', 'general')
#     print(category)
#     if category == 'general':
#         return render(request, 'category.html', {
#             'category': category,
#             'data': None  # or some data based on the category
#         })
    
# def search_protein(request):
#     category = request.GET.get('category', 'protein') 
#     print(category)
#     if category == 'protein':
#         data = Albumin.objects.filter(category='protein')
#         return render(request, "search_protein.html", {
#             'category': category,
#             'data': data,
#         })

def search_category(request):
    # print(category)
    category = request.GET.get('category', 'general')
    print(category)
    data = Albumin.objects.filter(category = category)
    print(data)
    if category == 'general':
        return render(request, 'category.html', {
            'category': category,
            'data': Albumin.objects.all()  
        })
    else:
        # Handle other categories
        return render(request, 'category.html', {
            'category': category,
            'data': data  # Replace with appropriate data for other categories
        })

def Databases(request, id):
    data = Albumin.objects.get(id=id)
    return render(request, "Albumin.html", {"data": data})

def new_file(request):
    return render(request, "Forms.html")

@login_required
def form_view(request):
    if request.method == 'POST':
        # Get category from hidden field or from the dropdown
        category = request.POST.get('category', 'general')

        # Retrieve other form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        subtitle = request.POST.get('subtitle')
        subcontent = request.POST.get('subcontent')
        image = request.FILES.get('image')

        # Check if subcontent exists and convert it back to a Python object
        if subcontent:
            subcontent = eval(subcontent)  # Convert the string back into a list of dicts

        # Create a new Albumin object and save to the database
        albumin = Albumin(
            title=title,
            description=description,
            sub_title=subtitle,
            sub_content=subcontent,
            image=image,
            category=category,
            updated_by=request.user  # Assuming user is logged in
        )
        albumin.save()

        # Redirect to a success page or home page
        return redirect('search_category')  # Redirect to search page or another success page

    else:
        # Render the form with initial category selected (optional)
        category = 'category'  # Default category for display
        return render(request, 'Forms.html', {'category': category})

# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']

#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             messages.success(request, 'Login successful!')
#             return redirect('home')  # Redirect to home page after successful login
#         else:
#             messages.error(request, 'Invalid username or password.')
#             return render(request, 'login.html')  # Re-render the login page with error message
#     else:
#         return render(request, 'login.html')  # Render login form for GET request

    # Ensure only authenticated users' details are passed to the template
    # user = None
    # if request.user.is_authenticated:
    #     user = CustomUser.objects.get(id=request.user.id)

    # return render(request, 'login.html', {'user': user})

UserModel = get_user_model()  # This is an alternative to directly using `settings.AUTH_USER_MODEL`

# def register(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         email = request.POST['email']
#         phone_number = request.POST['phone_number']
#         password1 = request.POST['password1']
#         password2 = request.POST['password2']
#         profile_picture = request.FILES.get('profile_picture')

#         if password1 != password2:
#             messages.error(request, "Passwords do not match!")
#             return redirect('register')

#         if UserModel.objects.filter(username=username).exists():
#             messages.error(request, "Username already exists!")
#             return redirect('register')

#         user = UserModel.objects.create_user(username=username, email=email, password=password1)
#         user.save()

#         # Save profile image
#         if profile_picture:
#             profile = Profile.objects.create(user=user, phone_number=phone_number, profile_picture=profile_picture)
#             profile.save()

#         messages.success(request, "Registration successful! Please log in.")
#         return redirect('login')

#     return render(request, 'register.html')

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("register")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        user = CustomUser.objects.create(username=username, email=email, phone_number=phone_number)
        user.password = make_password(password1)  # Hash password before saving
        user.save()

        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")

    return render(request, "register.html")


def user_login(request):
    image = None

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:  # Only allow superusers to log in
                login(request, user)
                return redirect('search_category')  # Redirect to the home page
            else:
                messages.error(request, 'Access restricted to superusers only.')
                return redirect('login')

        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')

    else:
        if request.user.is_authenticated:
            try:
                image = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                image = None  

        return render(request, 'login.html', {'image': image}) # Pass the image to the template
    
def logout_view(request):
    # Log the user out
    logout(request)
    # Redirect to the homepage or any other page
    return render(request, 'logout.html')  # or your desired URL

@login_required
def profile(request):
    user = request.user

    # Ensure the profile exists
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        try:
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
                profile.save()

            # Handle username update (Check for duplicates)
            new_username = request.POST.get('username')
            if new_username and new_username != user.username:
                if CustomUser.objects.filter(username=new_username).exclude(id=user.id).exists():
                    messages.error(request, "This username is already taken. Please choose another.")
                    return redirect('profile')
                user.username = new_username

            # Handle email update (Check for duplicates)
            new_email = request.POST.get('email')
            if new_email and new_email != user.email:
                if CustomUser.objects.filter(email=new_email).exclude(id=user.id).exists():
                    messages.error(request, "This email is already in use. Please use another.")
                    return redirect('profile')
                user.email = new_email

            # Handle password update
            new_password = request.POST.get('password')
            if new_password:
                user.set_password(new_password)  # Hash the new password before saving
                user.save()

                # Authenticate the user with the new password
                updated_user = authenticate(username=user.username, password=new_password)
                if updated_user:
                    login(request, updated_user)  # Log in the user with the new password
                    messages.success(request, "Profile updated successfully! Please log in again.")
                    return redirect('login')

            user.save()
            messages.success(request, "Profile updated successfully!")

            return redirect('profile')

        except IntegrityError:
            messages.error(request, "An error occurred while saving your profile. Please try again.")
            return redirect('profile')

    return render(request, 'profile.html')

def update_protein(request, id):
    data = Albumin.objects.get(id=id)
    print(data)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        sub_title = request.POST['subtitle']
        
        # Access the subcontent directly (it's already a list from the form)
        sub_content = json.loads(request.POST.get('subcontent', '[]'))
        
        # Check if the image is in the request files before accessing it
        image = request.FILES.get('image', None)

        # Update the model data with the new information
        data.title = title
        data.description = description
        data.sub_title = sub_title
        data.sub_content = sub_content
        
        # If there's a new image, update the image field
        if image:
            data.image = image
        
        # Save the updated data
        data.save()
        return redirect("search_category")
    return render(request, "update_protein.html", {'data': data})

def update_genome(request, id):
    data = Albumin.objects.get(id=id)
    print(data)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        sub_title = request.POST['subtitle']
        
        # Access the subcontent directly (it's already a list from the form)
        sub_content = json.loads(request.POST.get('subcontent', '[]'))
        
        # Check if the image is in the request files before accessing it
        image = request.FILES.get('image', None)

        # Update the model data with the new information
        data.title = title
        data.description = description
        data.sub_title = sub_title
        data.sub_content = sub_content
        
        # If there's a new image, update the image field
        if image:
            data.image = image
        
        # Save the updated data
        data.save()
        return redirect("search_category")
    return render(request, "update_genome.html", {'data': data})

def update_nucleotide(request, id):
    data = Albumin.objects.get(id=id)
    print(data)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        sub_title = request.POST['subtitle']
        
        # Access the subcontent directly (it's already a list from the form)
        sub_content = json.loads(request.POST.get('subcontent', '[]'))
        
        # Check if the image is in the request files before accessing it
        image = request.FILES.get('image', None)

        # Update the model data with the new information
        data.title = title
        data.description = description
        data.sub_title = sub_title
        data.sub_content = sub_content
        
        # If there's a new image, update the image field
        if image:
            data.image = image
        
        # Save the updated data
        data.save()
        return redirect("search_category")
    return render(request, "update_nucleotide.html", {'data': data})

def update_pubchem(request, id):
    data = Albumin.objects.get(id=id)
    print(data)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        sub_title = request.POST['subtitle']
        
        # Access the subcontent directly (it's already a list from the form)
        sub_content = json.loads(request.POST.get('subcontent', '[]'))
        
        # Check if the image is in the request files before accessing it
        image = request.FILES.get('image', None)

        # Update the model data with the new information
        data.title = title
        data.description = description
        data.sub_title = sub_title
        data.sub_content = sub_content
        
        # If there's a new image, update the image field
        if image:
            data.image = image
        
        # Save the updated data
        data.save()
        return redirect("search_category")
    return render(request, "update_pubchem.html", {'data': data})

def update_blast(request, id):
    data = Albumin.objects.get(id=id)
    print(data)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        sub_title = request.POST['subtitle']
        
        # Access the subcontent directly (it's already a list from the form)
        sub_content = json.loads(request.POST.get('subcontent', '[]'))
        
        # Check if the image is in the request files before accessing it
        image = request.FILES.get('image', None)

        # Update the model data with the new information
        data.title = title
        data.description = description
        data.sub_title = sub_title
        data.sub_content = sub_content
        
        # If there's a new image, update the image field
        if image:
            data.image = image
        
        # Save the updated data
        data.save()
        return redirect("search_category")
    return render(request, "update_blast.html", {'data': data})

def update_taxonomy(request, id):
    data = Albumin.objects.get(id=id)
    print(data)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        sub_title = request.POST['subtitle']
        
        # Access the subcontent directly (it's already a list from the form)
        sub_content = json.loads(request.POST.get('subcontent', '[]'))
        
        # Check if the image is in the request files before accessing it
        image = request.FILES.get('image', None)

        # Update the model data with the new information
        data.title = title
        data.description = description
        data.sub_title = sub_title
        data.sub_content = sub_content
        
        # If there's a new image, update the image field
        if image:
            data.image = image
        
        # Save the updated data
        data.save()
        return redirect("search_category")
    return render(request, "update_taxonomy.html", {'data': data})

def delete_protein(request, id):
    data=Albumin.objects.get(id=id)
    data.delete()
    return redirect("search_category")

def delete_genome(request, id):
    data=Albumin.objects.get(id=id)
    data.delete()
    return redirect("search_category")

def delete_nucleotide(request, id):
    data=Albumin.objects.get(id=id)
    data.delete()
    return redirect("search_category")

def delete_pubchem(request, id):
    data=Albumin.objects.get(id=id)
    data.delete()
    return redirect("search_category")

def delete_blast(request, id):
    data=Albumin.objects.get(id=id)
    data.delete()
    return redirect("search_category")

def delete_taxonomy(request, id):
    data=Albumin.objects.get(id=id)
    data.delete()
    return redirect("search_category")


