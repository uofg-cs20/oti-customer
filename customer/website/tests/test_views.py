from django.test import TestCase

from website.models import *
from website.helper_functions import getModes, getPurchases, getConcessions, getUsage, formatDate
from .test_fixtures import populate
from datetime import timedelta
import datetime
import pytz
from django.utils import timezone

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
        
    def test_purchase_displays_next_30_days_by_default(self):
        # Test the Purchase page with no filters - should be the next 30 days
        get_response = self.client.get('/purchases/')
        post_response = self.client.post('/purchases/', {"link":False})

        # Purchases passed in the request
        shown_get_purchases = get_response.context["purchases"]
        shown_post_purchases = get_response.context["purchases"]
        
        # Purchases that should have been filtered by the request
        customer = Customer.objects.get(user=get_response.context["user"])
        startdate = timezone.now()
        enddate = timezone.now() + timedelta(days=30)
        filtered_purchases = Purchase.objects.filter(customer_id=customer.id)
        # Filter by date, including all purchases whose "from-to" validity date range overlaps the filtered date range
        # First include those whose "from" date is within the filter range
        # Then include those whose "to" date is within the filter range
        # Finally include the special cases whose filter range is entirely within the "from-to" validity range
        filtered_purchases = filtered_purchases.filter(travel_to_date_time__range=[str(startdate), str(enddate)]) \
        .union(filtered_purchases.filter(travel_from_date_time__range=[str(startdate), str(enddate)])) \
        .union(filtered_purchases.filter(travel_from_date_time__lte=startdate, travel_to_date_time__gte=enddate))
        filtered_purchases = filtered_purchases.order_by('travel_to_date_time')
        
        self.assertEqual(list(shown_get_purchases), list(filtered_purchases), "Purchases shown by default from a GET request are not valid within the next 30 days")
        self.assertEqual(list(shown_post_purchases), list(filtered_purchases), "Purchases shown by default from a POST request with no filters are not valid within the next 30 days")
        
    def test_purchase_filters_after_given_date(self):
        response = self.client.post('/purchases/', {"startdate":(timezone.now()+timedelta(days=15)).strftime("%d-%m-%Y"), "link":False})

        # Purchases passed in the request
        shown_purchases = response.context["purchases"]
        
        # Purchases that should have been filtered by the request
        customer = Customer.objects.get(user=response.context["user"])
        startdate = timezone.now()+timedelta(days=15)
        enddate = datetime.datetime.max.replace(tzinfo=pytz.UTC)
        filtered_purchases = Purchase.objects.filter(customer_id=customer.id)
        # Filter by date, including all purchases whose "from-to" validity date range overlaps the filtered date range
        # First include those whose "from" date is within the filter range
        # Then include those whose "to" date is within the filter range
        # Finally include the special cases whose filter range is entirely within the "from-to" validity range
        filtered_purchases = filtered_purchases.filter(travel_to_date_time__range=[str(startdate), str(enddate)]) \
        .union(filtered_purchases.filter(travel_from_date_time__range=[str(startdate), str(enddate)])) \
        .union(filtered_purchases.filter(travel_from_date_time__lte=startdate, travel_to_date_time__gte=enddate))
        filtered_purchases = filtered_purchases.order_by('travel_to_date_time')
        
        self.assertEqual(list(shown_purchases), list(filtered_purchases), "Filtering after a given date does not display the correct Purchases")
        
        # Try filtering after a set date
        
        
        # Try filtering before a set date
        
        
        # Try filtering between 2 set dates
        
        

