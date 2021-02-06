from django.test import TestCase
from django.urls import reverse
from django import forms
from website.forms import *
from .test_fixtures_large import populate
from website.models import *
from django.contrib.auth import authenticate

class LoginTests(TestCase):
    
    def setUp(self):
        populate()
        
    def test_loginform_nonexistent_user(self):
        username = "bogus"
        password = "1234"
        
        form = LoginForm(data={"username":username, "password":password})
        self.assertFalse(form.is_valid())
        
        login = self.client.login(username=username, password=password)
        self.assertFalse(login)
        
    def test_loginform_wrong_password(self):
        username = "customer0"
        password = "wrong"
        
        form = LoginForm(data={"username":username, "password":password})
        self.assertFalse(form.is_valid())
        
        login = self.client.login(username=username, password=password)
        self.assertFalse(login)
        
    def test_loginform_correct_details(self):
        username = "customer0"
        password = "1234"
        
        form = LoginForm(data={"username":username, "password":password})
        self.assertTrue(form.is_valid())
        
        login = self.client.login(username=username, password=password)
        self.assertTrue(login)
        
        response = self.client.post(reverse("website:login"), {"username":username, "password":password})
        self.assertRedirects(response, reverse("website:purchases"))
        
    def test_loginform_cleaned_data(self):
        username = "customer0"
        password = "1234"
        
        form = LoginForm(data={"username":username, "password":password})
        loginName = ""
        loginPass = ""
        if form.is_valid():
            loginName = form.cleaned_data['username']
            loginPass = form.cleaned_data['password']
        self.assertEqual(loginName, username)
        self.assertEqual(loginPass, password)
        
        user = authenticate(username=loginName, password=loginPass)
        self.assertEqual(user, User.objects.get(username=username))
        