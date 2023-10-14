from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from store.models import Customer
from django.http import HttpResponse
from Account.models import Account
from Account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
import cv2
import os
import json
import base64
from django.core import files
from store.utils import cartData
TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"

def registration_view(request):
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'cartItems':cartItems}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            phone = form.cleaned_data.get('phone')
            Account = authenticate(email=email, password=raw_password)
            Customer.objects.create(
                user= Account,
                name = name,
                email = email,
                phone = phone,
                )
            login(request, Account)
            return redirect('store')
        else:
            context['registration_form'] = form
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'Account/register.html', context)

def logout_view(request):
    logout(request)
    return redirect("store")
 
def login_view(request):
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'cartItems':cartItems}
    user = request.user
    if user.is_authenticated:
        return redirect("store")
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect("store")
    else:
        form = AccountAuthenticationForm()
    context['login_form'] = form
    return render(request, "Account/login.html", context)

def account_view(request, *args, **kwargs):
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'cartItems':cartItems}
    user_id = kwargs.get("user_id")
    try:
        account = Account.objects.get(pk=user_id)
    except:
        return HttpResponse("Something went wrong.")
    if account:
        context['id'] = account.id
        context['username'] = account.username
        context['email'] = account.email
        context['profile_image'] = account.ImageURL
        context['hide_email'] = account.hide_email
        # Define template variables
        is_self = True
        user = request.user
        if user.is_authenticated and user != account:
            is_self = False
        elif not user.is_authenticated:
            Is_self = False
        # Set the template variables to the values
        context['is_self'] = is_self
        context['BASE_URL'] = settings.BASE_URL
        return render(request, "Account/account.html", context)

def edit_account_view(request, *args, **kwargs):
    data = cartData(request)
    cartItems = data['cartItems']
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = kwargs.get("user_id")
    account = Account.objects.get(pk=user_id)
    if account.pk != request.user.pk:
        return HttpResponse("You cannot edit someone elses profile.")
    context = {'cartItems':cartItems}
    if account:
            context['profile_image'] = account.ImageURL
    if request.POST:
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("account:view", user_id=account.pk)
        else:
            form = AccountUpdateForm(request.POST, instance=request.user,
                initial={
                    "id": account.pk,
                    "email": account.email,
                    "username": account.username,
                    "profile_image": account.profile_image,
                    "hide_email": account.hide_email,
                }
            )
            context['form'] = form
    else:
        form = AccountUpdateForm(
            initial={
                    "id": account.pk,
                    "email": account.email,
                    "username": account.username,
                    "profile_image": account.profile_image,
                    "hide_email": account.hide_email,
                }
            )
        context['form'] = form
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    return render(request, "Account/edit_account.html", context)

def save_temp_profile_image_from_base64String(imageString, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
            os.mkdir(settings.TEMP + "/" + str(user.pk))
        url = os.path.join(settings.TEMP + "/" + str(user.pk),TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(imageString)
        with storage.open('', 'wb+') as destination:
            destination.write(image)
            destination.close()
        return url
    except Exception as e:
        print("exception: " + str(e))
        # workaround for an issue I found
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imageString += "=" * ((4 - len(imageString) % 4) % 4)
            return save_temp_profile_image_from_base64String(imageString, user)
    return None
    
def crop_image(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.POST and user.is_authenticated:
        try:
            imageString = request.POST.get("image")
            url = save_temp_profile_image_from_base64String(imageString, user)
            img = cv2.imread(url)
            cropX = int(float(str(request.POST.get("cropX"))))
            cropY = int(float(str(request.POST.get("cropY"))))
            cropWidth = int(float(str(request.POST.get("cropWidth"))))
            cropHeight = int(float(str(request.POST.get("cropHeight"))))
            if cropX < 0:
                cropX = 0
            if cropY < 0: # There is a bug with cropperjs. y can be negative.
                cropY = 0
            crop_img = img[cropY:cropY+cropHeight, cropX:cropX+cropWidth]
            cv2.imwrite(url, crop_img)
            # Save the cropped image to user model
            user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
            user.save()
            payload['result'] = "success"
            payload['cropped_profile_image'] = user.profile_image.url
            # delete temp file
            os.remove(url)
        except Exception as e:
            print("exception: " + str(e))
            payload['result'] = "error"
            payload['exception'] = str(e)
    return HttpResponse(json.dumps(payload), content_type="application/json")

