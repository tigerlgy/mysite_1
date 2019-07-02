from django import forms
from django.contrib import auth
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="Username/E-mail",
        widget=forms.TextInput(
            attrs={'class':'form-control','placeholder':'Please enter your username or E-mail'}))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class':'form-control','placeholder':'Please enter your password'}))

    def clean(self):
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']
    
        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                if not user is None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('Either your username or password is incorrect')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data


class RegForm(forms.Form):
    username = forms.CharField(max_length=30,
        min_length=3,
        widget=forms.TextInput(
            attrs={'class':'form-control','placeholder':'Please enter your username'}))

    email = forms.EmailField(label='Email',
        widget=forms.EmailInput(
            attrs={'class':'form-control','placeholder':'Please enter your Email'}))

    password = forms.CharField(min_length=6,
        widget=forms.PasswordInput(
            attrs={'class':'form-control','placeholder':'Please enter your password'}))

    password_again = forms.CharField(label='Repeat Password',
        min_length=6,
        widget=forms.PasswordInput(
            attrs={'class':'form-control','placeholder':'Please enter your password again'}))

    verification_code = forms.CharField(
        label = 'Verification Code',
        required=False,
        widget=forms.TextInput(
            attrs={'class':'form-control','placeholder':"Please enter the verification code you've received"}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        code = self.request.session.get('register_code','')
        verification_code = self.cleaned_data.get('verification_code','')

        if not (code != '' and code == verification_code):
            raise forms.ValidationError('Your verification code is incorrect')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('The username already exist')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('The email has been registered')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('Please check your password again')
        return password_again

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code','').strip()
        if verification_code =='':
            raise forms.ValidationError('Verification code cannot be empty')
        return verification_code

class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(
        label='New Nickname',
        max_length=20,
        widget=forms.TextInput(
            attrs={'class':'form-control','placeholder':'Please enter your nickname'}
        )
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            forms.ValidationError('You are not logged in yet.')
        return self.cleaned_data


    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new','').strip()
        if nickname_new =='':
            raise ValidationError('Your nickname cannot be empty')
        return nickname_new
    
class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label = 'Email',
        widget=forms.EmailInput(
            attrs={'class':'form-control','placeholder':'Please enter your E-mail address'}))

    verification_code = forms.CharField(
        label = 'Verification Code',
        required=False,
        widget=forms.TextInput(
            attrs={'class':'form-control','placeholder':"Please enter the verification code you've received"}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('You are not logged in yet.')
        # if user has already linked an email
        if self.request.user.email != '':
            raise forms.ValidationError('You have linked an Email')

        code = self.request.session.get('bind_email_code','')
        verification_code = self.cleaned_data.get('verification_code','')

        if not (code != '' and code == verification_code):
            raise forms.ValidationError('Your verification code is incorrect')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This Email address has already been linked')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code','').strip()
        if verification_code =='':
            raise forms.ValidationError('Verification code cannot be empty')
        return verification_code

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class':'form-control','placeholder':'Please enter your old password'}))

    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class':'form-control','placeholder':'Please enter your new password'}))

    new_password_again = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class':'form-control','placeholder':'Please re-enter your new password'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        # test if the new passwords are idntical
        new_password = self.cleaned_data.get('new_password','')
        new_password_again = self.cleaned_data.get('new_password_again','')
        if new_password != new_password_again or new_password =='':
            raise forms.ValidationError('Please make sure your inputs are the same')
        return self.cleaned_data

    def clean_old_password(self):
        # test if the old password is correct
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Your old password is incorrect')
        return old_password


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label = 'Email',
        widget=forms.EmailInput(
            attrs={'class':'form-control','placeholder':'Please enter your E-mail address'}))

    verification_code = forms.CharField(
        label = 'Verification Code',
        required=False,
        widget=forms.TextInput(
            attrs={'class':'form-control','placeholder':"Please enter the verification code you've received"}))

    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class':'form-control','placeholder':'Please enter your new password'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email= self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('E-mail does not exist')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code','').strip()
        if verification_code =='':
            raise forms.ValidationError('Verification code cannot be empty')

        code = self.request.session.get('forgot_password_code','')
        verification_code = self.cleaned_data.get('verification_code','')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('Your verification code is incorrect')

        return verification_code
