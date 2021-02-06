from django.test import TestCase

from website.models import *
from website.apps import WebsiteConfig
from website.helper_functions import getModes, getPurchases, getConcessions, getUsage, formatDate
from .test_fixtures_large import populate
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
        
    def test_apps(self):
        self.assertEqual(WebsiteConfig.name, 'website')
        
        
class AuthenticationTests(TestCase):

    def setUp(self):
        populate()
        
    def test_connect_redirect_if_not_logged_in(self):
        response = self.client.get('/connect/')
        self.assertRedirects(response, '/')
    
    def test_connect_redirect_if_not_logged_in(self):
        response = self.client.get('/connect/')
        self.assertRedirects(response, '/')
        
    def test_purchase_redirect_if_not_logged_in(self):
        response = self.client.get('/purchases/')
        self.assertRedirects(response, '/')
        
    def test_concession_redirect_if_not_logged_in(self):
        response = self.client.get('/concessions/')
        self.assertRedirects(response, '/')
        
    def test_usage_redirect_if_not_logged_in(self):
        response = self.client.get('/usage/')
        self.assertRedirects(response, '/')
        
    def test_login_redirect_if_logged_in(self):
        login = self.client.login(username='customer0', password='1234')
        response = self.client.get('/')
        self.assertRedirects(response, '/purchases/')
        
    def test_logout(self):
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/')
        

class PurchaseTests(TestCase):

    def setUp(self):
        populate()
        login = self.client.login(username='customer0', password='1234')
        
    def test_purchase_uses_correct_template(self):
        response = self.client.get('/purchases/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/purchases.html')
        
    def test_purchase_mode_filter(self):
        # Make an example request to the Purchase page
        context = {"mode": Mode.objects.get(short_desc="Train")}
        response = self.client.post('/purchases/', context)
        
        # Test that the mode filter works correctly
        purchases = response.context["purchases"]
        self.assertTrue([p.mode.short_desc == response.context["mode"] for p in purchases] or not purchases, "Not all Purchases have been filtered by the correct mode")
        
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
                
    def test_purchase_filters_before_given_date(self):
        response = self.client.post('/purchases/', {"enddate":(timezone.now()-timedelta(days=5)).strftime("%d-%m-%Y"), "link":False})

        # Purchases passed in the request
        shown_purchases = response.context["purchases"]
        
        # Purchases that should have been filtered by the request
        customer = Customer.objects.get(user=response.context["user"])
        enddate = timezone.now()-timedelta(days=5)
        startdate = datetime.datetime.min.replace(tzinfo=pytz.UTC)
        filtered_purchases = Purchase.objects.filter(customer_id=customer.id)
        # Filter by date, including all purchases whose "from-to" validity date range overlaps the filtered date range
        # First include those whose "from" date is within the filter range
        # Then include those whose "to" date is within the filter range
        # Finally include the special cases whose filter range is entirely within the "from-to" validity range
        filtered_purchases = filtered_purchases.filter(travel_to_date_time__range=[str(startdate), str(enddate)]) \
        .union(filtered_purchases.filter(travel_from_date_time__range=[str(startdate), str(enddate)])) \
        .union(filtered_purchases.filter(travel_from_date_time__lte=startdate, travel_to_date_time__gte=enddate))
        filtered_purchases = filtered_purchases.order_by('travel_to_date_time')
        
        self.assertEqual(list(shown_purchases), list(filtered_purchases), "Filtering before a given date does not display the correct Purchases")
        
    def test_purchase_filters_between_given_dates(self):
        response = self.client.post('/purchases/', {"startdate":(timezone.now()+ timedelta(days=15)).strftime("%d-%m-%Y"), "enddate":(timezone.now()+timedelta(days=100)).strftime("%d-%m-%Y"), "link":False})

        # Purchases passed in the request
        shown_purchases = response.context["purchases"]
        
        # Purchases that should have been filtered by the request
        customer = Customer.objects.get(user=response.context["user"])
        enddate = timezone.now()+timedelta(days=100)
        startdate = timezone.now()+ timedelta(days=15)
        filtered_purchases = Purchase.objects.filter(customer_id=customer.id)
        # Filter by date, including all purchases whose "from-to" validity date range overlaps the filtered date range
        # First include those whose "from" date is within the filter range
        # Then include those whose "to" date is within the filter range
        # Finally include the special cases whose filter range is entirely within the "from-to" validity range
        filtered_purchases = filtered_purchases.filter(travel_to_date_time__range=[str(startdate), str(enddate)]) \
        .union(filtered_purchases.filter(travel_from_date_time__range=[str(startdate), str(enddate)])) \
        .union(filtered_purchases.filter(travel_from_date_time__lte=startdate, travel_to_date_time__gte=enddate))
        filtered_purchases = filtered_purchases.order_by('travel_to_date_time')
        
        self.assertEqual(list(shown_purchases), list(filtered_purchases), "Filtering between two given dates does not display the correct Purchases")
        
    def test_formatDate_correctly_formats_dates(self):
        formatted_date = formatDate("22-05-2017")
        self.assertEqual(formatted_date.year, 2017)
        self.assertEqual(formatted_date.month, 5)
        self.assertEqual(formatted_date.day, 22)
        
class ConcessionTests(TestCase):

    def setUp(self):
        populate()
        login = self.client.login(username='customer0', password='1234')
        
    def test_concession_uses_correct_template(self):
        response = self.client.get('/concessions/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/concessions.html')
        
    def test_concession_mode_filter(self):
        # Make an example request to the Concessions page
        context = {"mode":Mode.objects.get(short_desc="Bus")}
        response = self.client.post('/concessions/', context)
        
        # Test that the mode filter works correctly
        concessions = response.context["concessions"]
        self.assertTrue([c.mode.short_desc == response.context["mode"] for c in concessions] or not concessions, "Not all concessions have been filtered by the correct mode")
        
    def test_concession_displays_valid_concessions_by_default(self):
        # Test the concession page with no filters - should show valid concessions
        get_response = self.client.get('/concessions/')
        post_response = self.client.post('/concessions/', {"link":False})

        # concessions passed in the request
        shown_get_concessions = get_response.context["concessions"]
        shown_post_concessions = get_response.context["concessions"]
        
        # concessions that should have been filtered by the request
        customer = Customer.objects.get(user=get_response.context["user"])
        filtered_concessions = Concession.objects.filter(valid_to_date_time__gt=timezone.now(), customer_id=customer.id)
        
        self.assertEqual(list(shown_get_concessions), list(filtered_concessions), "Not all Concessions shown by default from a GET request are valid")
        self.assertEqual(list(shown_post_concessions), list(filtered_concessions), "Not all Concessions shown by default from a POST request with no filters are valid")
        
    def test_concession_valid_filter(self):
        response = self.client.post('/concessions/', {"status":"valid", "link":False})

        # concessions passed in the request
        shown_concessions = response.context["concessions"]
        
        # concessions that should have been filtered by the request
        customer = Customer.objects.get(user=response.context["user"])
        filtered_concessions = Concession.objects.filter(valid_to_date_time__gt=timezone.now(), customer_id=customer.id)
        
        self.assertEqual(list(shown_concessions), list(filtered_concessions), "Valid filter does not display the correct Concessions")
        
    def test_concession_expired_filter(self):
        response = self.client.post('/concessions/', {"status":"past", "link":False})

        # concessions passed in the request
        shown_concessions = response.context["concessions"]
        
        # concessions that should have been filtered by the request
        customer = Customer.objects.get(user=response.context["user"])
        filtered_concessions = Concession.objects.filter(valid_to_date_time__lt=timezone.now(), customer_id=customer.id)
        
        self.assertEqual(list(shown_concessions), list(filtered_concessions), "Expired filter does not display the correct Concessions")
        
class UsageTests(TestCase):

    def setUp(self):
        populate()
        login = self.client.login(username='customer0', password='1234')
        
    def test_usage_uses_correct_template(self):
        response = self.client.get('/usage/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/usage.html')
        
    def test_usage_mode_filter(self):
        response = self.client.post('/usage/', {"mode":Mode.objects.get(short_desc="Bus"), "startdate":(timezone.now()-timedelta(days=750)).strftime("%d-%m-%Y"), "enddate":timezone.now().strftime("%d-%m-%Y"), "link":False})

        # Usages passed in the request
        shown_usage = list(response.context.get("usages", []))
        
        # Usages that should have been filtered by the request
        customer = Customer.objects.get(user=response.context["user"])
        startdate = timezone.now()-timedelta(days=750)
        enddate = timezone.now()
        filtered_usages = Usage.objects.filter(customer=customer.id, mode=Mode.objects.get(short_desc="Bus"))
        # Filter by date, including all usages whose "from-to" validity date range overlaps the filtered date range
        # First include those whose "from" date is within the filter range
        # Then include those whose "to" date is within the filter range
        # Finally include the special cases whose filter range is entirely within the "from-to" validity range
        filtered_usages = filtered_usages.filter(travel_to__date_time__range=[str(startdate), str(enddate)]) \
        .union(filtered_usages.filter(travel_from__date_time__range=[str(startdate), str(enddate)])) \
        .union(filtered_usages.filter(travel_from__date_time__lte=startdate, travel_to__date_time__gte=enddate))
        
        self.assertEqual(shown_usage, list(filtered_usages), "Filtering by mode does not display the correct Usages")
        
    def test_usage_date_filters(self):
        response = self.client.post('/usage/', {"startdate":(timezone.now()-timedelta(days=1000)).strftime("%d-%m-%Y"), "enddate":(timezone.now()-timedelta(days=500)).strftime("%d-%m-%Y"), "link":False})

        # Usages passed in the request
        shown_usage = list(response.context.get("usages", []))
        
        # Usages that should have been filtered by the request
        customer = Customer.objects.get(user=response.context["user"])
        startdate = timezone.now()-timedelta(days=1000)
        enddate = timezone.now()-timedelta(days=500)
        filtered_usages = Usage.objects.filter(customer=customer.id)
        # Filter by date, including all usages whose "from-to" validity date range overlaps the filtered date range
        # First include those whose "from" date is within the filter range
        # Then include those whose "to" date is within the filter range
        # Finally include the special cases whose filter range is entirely within the "from-to" validity range
        filtered_usages = filtered_usages.filter(travel_to__date_time__range=[str(startdate), str(enddate)]) \
        .union(filtered_usages.filter(travel_from__date_time__range=[str(startdate), str(enddate)])) \
        .union(filtered_usages.filter(travel_from__date_time__lte=startdate, travel_to__date_time__gte=enddate))
        
        self.assertEqual(shown_usage,list(filtered_usages), "Filtering between given dates does not display the correct Usages")
        

