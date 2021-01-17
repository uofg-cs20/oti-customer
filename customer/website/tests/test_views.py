from django.test import TestCase

from website.models import *
from website.helper_functions import getModes, getPurchases, getConcessions, getUsage 
from .test_fixtures import populate

# views/helper functions will be tested here

class CustomerTests(TestCase):
    
    def setUp(self):
        # create customer
        populate()

    def test_get_modes(self):
        modes = getModes()
        self.assertEqual(len(modes), 3)
        

class PurchaseTests(TestCase):

    def setUp(self):
        populate()
        login = self.client.login(username='customer', password='1234')
        
    def test_purchase_uses_correct_template(self):
        response = self.client.get('/purchases/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/purchases.html')
        
    def test_purchase_mode_filter(self):
        # Make an example request to the Purchase page
        context = {"mode":Mode.objects.get(short_desc="Train")}
        response = self.client.post('/purchases/', context)
        
        # Test that the mode filter works correctly
        purchases = response.context["purchases"]
        self.assertEqual(set([True]), set([p.mode.short_desc == response.context["mode"] for p in purchases]), "Not all Purchases have been filtered by the correct mode")
        

