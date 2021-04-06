from django.test import TestCase
from website.models import TravelClass, Ticket, RecordID, Mode

# tests the model structure (field labels and max length)

class TravelClassTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        TravelClass.objects.create(travel_class="first")

    def test_travel_class_label(self):
        travel_class = TravelClass.objects.get(travel_class="first")
        field_label = travel_class._meta.get_field('travel_class').verbose_name
        self.assertEqual(field_label, 'travel class')

    def test_travel_class_max_length(self):
        travel_class = TravelClass.objects.get(travel_class="first")
        max_length = travel_class._meta.get_field('travel_class').max_length
        self.assertEqual(max_length, 50)

    def test_travel_class_str(self):
        travel_class = TravelClass.objects.get(travel_class="first")
        self.assertEqual(str(travel_class), travel_class.travel_class)


class TicketTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Ticket.objects.create(reference="AAA34135", number_usages="one", reference_type="reference type", medium="train")

    def test_ticket_reference_label(self):
        ticket = Ticket.objects.get(reference="AAA34135")
        field_label = ticket._meta.get_field('reference').verbose_name
        self.assertEqual(field_label, 'reference')

    def test_ticket_number_usages_label(self):
        ticket = Ticket.objects.get(reference="AAA34135")
        field_label = ticket._meta.get_field('number_usages').verbose_name
        self.assertEqual(field_label, 'number usages')

    def test_ticket_reference_type_label(self):
        ticket = Ticket.objects.get(reference="AAA34135")
        field_label = ticket._meta.get_field('reference_type').verbose_name
        self.assertEqual(field_label, 'reference type')

    def test_ticket_medium_label(self):
        ticket = Ticket.objects.get(reference="AAA34135")
        field_label = ticket._meta.get_field('medium').verbose_name
        self.assertEqual(field_label, 'medium')

    def test_ticket_reference_max_length(self):
        ticket = Ticket.objects.get(reference="AAA34135")
        max_length = ticket._meta.get_field('reference').max_length
        self.assertEqual(max_length, 30)

    def test_ticket_number_usages_max_length(self):
        ticket = Ticket.objects.get(reference="AAA34135")
        max_length = ticket._meta.get_field('number_usages').max_length
        self.assertEqual(max_length, 3)

    def test_ticket_reference_type_max_length(self):
        ticket = Ticket.objects.get(reference="AAA34135")
        max_length = ticket._meta.get_field('reference_type').max_length
        self.assertEqual(max_length, 30)

    def test_ticket_medium_max_length(self):
        ticket = Ticket.objects.get(reference="AAA34135")
        max_length = ticket._meta.get_field('medium').max_length
        self.assertEqual(max_length, 20)

    def test_ticket_str(self):
        ticket = Ticket.objects.get(reference="AAA34135")
        self.assertEqual(str(ticket), ticket.reference)


class RecordIDTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        RecordID.objects.create(id="1000000")

    def test_record_id_label(self):
        record = RecordID.objects.get(id="1000000")
        field_label = record._meta.get_field('id').verbose_name
        self.assertEqual(field_label, 'id')

    def test_record_id_max_length(self):
        record = RecordID.objects.get(id="1000000")
        max_length = record._meta.get_field('id').max_length
        self.assertEqual(max_length, 100)

    def test_record_id_str(self):
        record = RecordID.objects.get(id="1000000")
        self.assertEqual(str(record), record.id)


class ModeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Mode.objects.create(id="train", short_desc="train mode", long_desc="this is train mode")

    def test_mode_id_label(self):
        train = Mode.objects.get(id="train")
        field_label = train._meta.get_field('id').verbose_name
        self.assertEqual(field_label, 'id')

    def test_mode_short_desc_label(self):
        train = Mode.objects.get(id="train")
        field_label = train._meta.get_field('short_desc').verbose_name
        self.assertEqual(field_label, 'short desc')

    def test_mode_long_desc_label(self):
        train = Mode.objects.get(id="train")
        field_label = train._meta.get_field('long_desc').verbose_name
        self.assertEqual(field_label, 'long desc')

    def test_mode_id_max_length(self):
        train = Mode.objects.get(id="train")
        max_length = train._meta.get_field('id').max_length
        self.assertEqual(max_length, 10)

    def test_mode_short_desc_max_length(self):
        train = Mode.objects.get(id="train")
        max_length = train._meta.get_field('short_desc').max_length
        self.assertEqual(max_length, 50)

    def test_mode_long_desc_max_length(self):
        train = Mode.objects.get(id="train")
        max_length = train._meta.get_field('long_desc').max_length
        self.assertEqual(max_length, 8000)

    def test_mode_str(self):
        train = Mode.objects.get(id="train")
        self.assertEqual(str(train), train.short_desc)