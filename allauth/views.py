from django.shortcuts import redirect, render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from .utils import token_generater
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading

# class EmailThread(threading.Thread):
#     def __init__(self, email):
#         self.email = email
#         threading.Thread.__init__(self)

#     def run(self):
#         self.email.send(fail_silently=True)


class Registration(View):
    def get(self, request):
        return render(request, 'allauth/register.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'FieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():

                if len(password) < 8:
                    messages.error(request, 'Password too short')
                    return render(request, 'allauth/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = True  # allow login without email verification
                user.save()

                messages.success(request, 'Account successfully created. You can now log in.')
                return redirect('login')  # or wherever you want to send the user

        messages.error(request, 'Username or email already exists.')
        return render(request, 'allauth/register.html', context)



class UsernameValidation(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error':'Usernmae should only contain alphanumeric characters'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Sorry usernmae is already taken'})
        return JsonResponse({'username_valid':True})


class EmailValidation(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'})
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'Sorry email is already registered'})
        return JsonResponse({'email_valid':True})

class Verification(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if not token_generater.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')
            if user.is_active:
                return redirect('login')
            user.is_active=True
            user.save()
            messages.success(request, 'Acccount activated successfully')
            return redirect('login')

        except Exception as e:
            print(e)

        return redirect('login')


class Login(View):
    def get(self, request):
        return render(request, 'allauth/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome '+user.username+' You are now loggined')
                    return redirect('dashboard-lastmonth')

                messages.error(request, 'Account is not activated, Please check your email')
                return render(request, 'allauth/login.html')
            messages.error(request, 'Invalid credintails, try again')
            return render(request, 'allauth/login.html')

        messages.error(request, 'Please fill all fields')
        return render(request, 'allauth/login.html')

class Logout(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')

class ResetPassword(View):
    def get(self, request):
        return render(request, 'allauth/reset_password.html')


    def post(self, request):
        email = request.POST['email']
        context = {
            'values':request.POST
        }
        if not validate_email(email):
            messages.error(request, 'Email is not valid')
            return render(request, 'allauth/reset_password.html', context)

        user = User.objects.filter(email=email)

        if user.exists():
            uidb64 = urlsafe_base64_encode(force_bytes(user[0].pk))
            domain = get_current_site(request).domain
            link = reverse('reset-user-password', kwargs={'uidb64':uidb64, 'token':PasswordResetTokenGenerator().make_token(user[0])})
            reset_url = 'http://'+domain+link
            email_subject = 'Reset Password Link'
            email_body = "Hi there, \n Please use this link to Reset your Password\n" +reset_url
            email = EmailMessage(
                email_subject,
                email_body,
                '202305442mar.venkatswaroope3@gmail.com',
                [email],
            )
            
        messages.error(request, 'Email not registered, Please try again')
        return render(request, 'allauth/reset_password.html', context)

class CompleteResetPassword(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
        if not PasswordResetTokenGenerator().check_token(user, token):
            messages.info(request, 'Password reset link is invalid, Please request again')
            return render(request, 'allauth/reset_password.html')

        return render(request, 'allauth/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token,
            'values':request.POST
        }
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Password donot match')
            return render(request, 'allauth/set-new-password.html', context)
        if len(password)<8:
            messages.error(request, 'Password too short')
            return render(request, 'allauth/set-new-password.html', context)

        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)

        if user:
            user.set_password(password)
            user.save()
            messages.success(request, 'Password Reset successfully, You can login with new credintials')
            return redirect('login')


        messages.error(request, 'Password Reset link Not Valid')
        return render(request, 'allauth/set-new-password.html', context)
