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
