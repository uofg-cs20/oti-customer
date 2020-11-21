from django import forms
from .models import Mode
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegisterForm(forms.Form):
    pass

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-group'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'form-group'}))

    def clean(self):
        loginName = self.cleaned_data['username']
        loginPass = self.cleaned_data['password']

        # check the given user is in our database
        if not User.objects.filter(username=loginName).exists():
            raise forms.ValidationError("We could not find an account with this username.")

        # check the password matches
        if not authenticate(username=loginName, password=loginPass):
            raise forms.ValidationError("Incorrect Password.")

        return self.cleaned_data

class ConnectForm(forms.Form):
    pass
