from django.test import TestCase
from website.models import *
from datetime import timedelta
import datetime
import pytz
import json
from django.utils import timezone

from .test_fixtures_large import populate

# --- TEST PARAMETERS -------------------
api_url = "/api/"
default_pagination = 5
test_user_username = "customer0"
test_user_password = "1234"
# ---------------------------------------
    
purchases_url = api_url + "purchase/"
concessions_url = api_url + "concession/"
usages_url = api_url + "usage/"

# Common testing functions
def set_up_tests(testobj):
    populate()
    login = testobj.client.login(username=test_user_username, password=test_user_password)

def api_page_response(testobj, page_url):
    response = testobj.client.get(page_url)
    return response

# Unit tests for the Customer API
class APIPurchaseTests(TestCase):

    def setUp(self):
        set_up_tests(self)
        
    def test_api_purchases_exists_at_desired_location(self):
        self.assertEqual(api_page_response(self, purchases_url).status_code, 200)
        
    def test_api_purchases_default_pagination(self):
        self.assertTrue(len(api_page_response(self, purchases_url).data) <= default_pagination)
        
    def test_api_purchases_correct_user(self):
        self.assertTrue(Purchase.objects.get(id=p['id']).customer == Customer.objects.get(user=User.objects.get(username=test_user_username)) for p in api_page_response(self, purchases_url).data)
        
class APIConcessionTests(TestCase):

    def setUp(self):
        set_up_tests(self)
        
    def test_api_concessions_exists_at_desired_location(self):
        self.assertEqual(api_page_response(self, concessions_url).status_code, 200)
        
    def test_api_purchases_default_pagination(self):
        self.assertTrue(len(api_page_response(self, concessions_url).data) <= default_pagination)
        
    def test_api_concessions_correct_user(self):
        self.assertTrue(Concession.objects.get(id=c['id']).customer == Customer.objects.get(user=User.objects.get(username=test_user_username)) for c in api_page_response(self, concessions_url).data)
       
class APIUsageTests(TestCase):

    def setUp(self):
        set_up_tests(self)
        
    def test_api_usages_exists_at_desired_location(self):
        self.assertEqual(api_page_response(self, usages_url).status_code, 200)
        
    def test_api_usages_default_pagination(self):
        self.assertTrue(len(api_page_response(self, usages_url).data) <= default_pagination)
        
    def test_api_usages_correct_user(self):
        self.assertTrue(Usage.objects.get(id=u['id']).customer == Customer.objects.get(user=User.objects.get(username=test_user_username)) for u in api_page_response(self, usages_url).data)

