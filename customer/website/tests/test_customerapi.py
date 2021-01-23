from django.test import TestCase

from website.models import *
from .test_fixtures_large import populate
from datetime import timedelta
import datetime
import pytz
from django.utils import timezone

# Unit tests for the Customer API
        
class APIPurchaseTests(TestCase):

    def setUp(self):
        populate()
        login = self.client.login(username='customer0', password='1234')
        
    def test_api_purchases_exists_at_desired_location(self):
        response = self.client.get('/api/purchases/')
        self.assertEqual(response.status_code, 200)
        
    def test_pagination_is_five(self):
        response = self.client.get('/api/purchases/')
        self.assertTrue(len(response.data) <= 5)
        
    

