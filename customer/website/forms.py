from django import forms
from .models import Mode
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())


    def clean_confirm_password(self):
        password1 = self.cleaned_data['password']
        password2 = self.cleaned_data['confirm_password']

        if not password1 == password2:
            raise forms.ValidationError("The passwords do not match.")
        return password2

    def clean_email(self):
        email = self.cleaned_data['email'].strip()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password', 'confirm_password')



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

