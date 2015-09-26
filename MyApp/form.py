from django import forms
from .models import *
from captcha.fields import CaptchaField
from django.forms.extras import SelectDateWidget

class SignupForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    birthday = forms.DateField(widget=SelectDateWidget(years=range(2015,1900,-1)))

    class Meta:
        model = Person
        fields = ['username', 'password', 'first_name', 'last_name', 'birthday', 'email']
