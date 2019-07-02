import string
import random
import time
from django.shortcuts import render_to_response, render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm,ChangePasswordForm,ForgotPasswordForm
from .models import Profile


def login_for_modal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def login(request):
    if request.method =="POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request, 'user/login.html', context)

def register(request):
    if request.method =="POST":
        reg_form = RegForm(request.POST,request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            #Register new user
            user = User.objects.create_user(username, email, password)
            user.save()
            #CLear session
            del request.session['register_code']
            #Auto login new user
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        reg_form = RegForm()

    context = {}
    context['reg_form'] = reg_form
    return render(request, 'user/register.html', context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))

def user_info(request):
    context = {}
    return render(request,'user/user_info.html', context)

def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method =="POST":
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)

    else:
        form = ChangeNicknameForm()
    context = {}
    context['page_title'] = 'Edit Nickname'
    context['form_title'] = 'Edit Nickname'
    context['submit_text'] = 'Change'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)

def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method =="POST":
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            #Clear session
            del request.session['bind_email_code']
            return redirect(redirect_to)

    else:
        form = BindEmailForm()
    context = {}
    context['page_title'] = 'Link your E-mail'
    context['form_title'] = 'Link your E-mail'
    context['submit_text'] = 'Link E-mail'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/bind_email.html', context)

def send_verification_code(request):
    email = request.GET.get('email','')
    data = {}
    send_for = request.GET.get('send_for','')
    if email != '':
        # Generate random verification code
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time',0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        # Send Email
        else:
            request.session[send_for] = code
            request.session['send_code_time'] = now

            send_mail(
                'Your Verification Code',
                'Your Verification Code: %s' % code,
                'guangyuan.liu@ngaa.com.cn',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def change_password(request):
    redirect_to = reverse('home')
    if request.method =="POST":
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            return redirect(redirect_to)

    else:
        form = ChangePasswordForm()

    context = {}
    context['page_title'] = 'Change Password'
    context['form_title'] = 'Change Password'
    context['submit_text'] = 'Change'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)

def forgot_password(request):
    redirect_to = reverse('home')
    if request.method =="POST":
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            #Clear session
            del request.session['forgot_password_code']
            return redirect(redirect_to)

    else:
        form = ForgotPasswordForm()
    context = {}
    context['page_title'] = 'Reset password'
    context['form_title'] = 'Reset password'
    context['submit_text'] = 'Reset'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/forgot_password.html', context)
