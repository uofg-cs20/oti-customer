from django.test import TestCase
from website.models import *
from datetime import timedelta
from django.utils import timezone

from .fixtures import populate

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

def api_page_response(testobj, page_url, queryparams=None):
    response = testobj.client.get(page_url, queryparams)
    return response
    
# Unit tests for the Customer API
class APIPurchaseTests(TestCase):
    def setUp(self):
        set_up_tests(self)
        
    def test_api_purchase_exists_at_desired_location(self):
        self.assertEqual(api_page_response(self, purchases_url).status_code, 200)
        
    def test_api_purchase_default_pagination(self):
        self.assertTrue(len(api_page_response(self, purchases_url).data) <= default_pagination, "The API purchase page does not have the correct default pagination")
        
    def test_api_purchase_correct_user(self):
        self.assertTrue(all([Purchase.objects.get(id=p['id']).customer == Customer.objects.get(user=User.objects.get(username=test_user_username)) for p in api_page_response(self, purchases_url).data]), "Not all displayed purchases are owned by the correct user")
        
    def test_api_purchase_filterstring(self):
        filterString = "1"
        self.assertTrue(all([filterString in p['id'] for p in api_page_response(self, purchases_url, {"filterString":[filterString]}).data]), "Querying the API with a filterString does not return the correct purchases")
        
    def test_api_purchase_travel_valid_during(self):
        startdate = timezone.now() + timedelta(days=2)
        enddate = timezone.now() + timedelta(days=50)
        self.assertTrue(all([p.get("travel-to-date-time")>=startdate and p.get("travel-from-date-time")<=enddate for p in api_page_response(self, purchases_url, {"travel_valid_during_from":startdate, "travel_valid_during_to":enddate}).data]), "Querying the API with travel_valid_during_from and travel_valid_during_to does not return the correct purchases")
        
class APIConcessionTests(TestCase):
    def setUp(self):
        set_up_tests(self)
        
    def test_api_concession_exists_at_desired_location(self):
        self.assertEqual(api_page_response(self, concessions_url).status_code, 200)
        
    def test_api_purchase_default_pagination(self):
        self.assertTrue(len(api_page_response(self, concessions_url).data) <= default_pagination)
        
    def test_api_concession_correct_user(self):
        self.assertTrue(all([Concession.objects.get(id=c['id']).customer == Customer.objects.get(user=User.objects.get(username=test_user_username)) for c in api_page_response(self, concessions_url).data]), "Not all displayed concessions are owned by the correct user")
    
    def test_api_concession_filterstring(self):
        filterString = "1"
        self.assertTrue(all([filterString in c['id'] for c in api_page_response(self, concessions_url, {"filterString":[filterString]}).data]), "Querying the API with a filterString does not return the correct concessions")
    
    def test_api_concession_concession_valid_during(self):
        startdate = timezone.now() + timedelta(days=2)
        enddate = timezone.now() + timedelta(days=50)
        self.assertTrue(all([c.get("valid-to-date-time")>=startdate and c.get("valid-from-date-time")<=enddate for c in api_page_response(self, concessions_url, {"concession_valid_during_from":startdate, "concession_valid_during_to":enddate}).data]), "Querying the API with concession_valid_during_from and concession_valid_during_to does not return the correct concessions")
        
class APIUsageTests(TestCase):
    def setUp(self):
        set_up_tests(self)
        
    def test_api_usage_exists_at_desired_location(self):
        self.assertEqual(api_page_response(self, usages_url).status_code, 200)
        
    def test_api_usage_default_pagination(self):
        self.assertTrue(len(api_page_response(self, usages_url).data) <= default_pagination)
        
    def test_api_usage_correct_user(self):
        self.assertTrue(all([Usage.objects.get(id=u['id']).customer == Customer.objects.get(user=User.objects.get(username=test_user_username)) for u in api_page_response(self, usages_url).data]), "Not all displayed usages are associated with the correct user")

    def test_api_usage_filterstring(self):
        filterString = "1"
        self.assertTrue(all([filterString in u['id'] for u in api_page_response(self, usages_url, {"filterString":[filterString]}).data]), "Querying the API with a filterString does not return the correct usages")
    
    def test_api_usage_usage_occurred_during(self):
        startdate = timezone.now() - timedelta(days=100)
        enddate = timezone.now() - timedelta(days=2)
        self.assertTrue(all([u.get("travel-to").get("date-time")>=startdate and u.get("travel_from").get("date-time")<=enddate for u in api_page_response(self, usages_url, {"usage_occurred_during_from":startdate, "usage_occurred_during_to":enddate}).data]), "Querying the API with usage_occurred_during_from and usage_occurred_during_to does not return the correct usages")
        
