from django.contrib import admin

from .models import *

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id',)

class AccountAdmin(admin.ModelAdmin):
    list_display = ('operator_id', 'customer')

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'mode', 'travel_class', 'booking_date_time', 'transaction', 'account_balance', 'agent', 'passenger_number', 'passenger_type', 'vehicle', 'route', 'travel_from_date_time', 'travel_to_date_time', 'conditions', 'concession', 'restrictions', 'ticket', 'location_from', 'location_to', 'reserved_position', 'service_request', 'customer_id')

class LocationAdmin(admin.ModelAdmin):
    list_display = ('lat_long', 'NaPTAN', 'other', 'other_type', 'accuracy')

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('included', 'reference', 'vehicle_type', 'conditions')

class LatitudeLongitudeAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude')

class MonetaryValueAdmin(admin.ModelAdmin):
    list_display = ('amount', 'currency')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'payment_type', 'payment_method', 'price')

class DiscountAdmin(admin.ModelAdmin):
    list_display = ('discount_type', 'discount_value', 'discount_description')

class ConcessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'discount', 'transaction', 'valid_from_date_time', 'valid_to_date_time', 'conditions', 'customer')

class UsageAdmin(admin.ModelAdmin):
    list_display = ('id', 'mode', 'reference', 'travel_class', 'travel_from', 'travel_to', 'purchase_id', 'route_via_avoid', 'ticket_reference', 'pre_paid', 'price', 'customer_id')

class UsageReferenceAdmin(admin.ModelAdmin):
    list_display = ('reference', 'reference_type')

class UsageFromToAdmin(admin.ModelAdmin):
    list_display = ('location', 'date_time', 'reference')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'unit', 'amount', 'price', 'usage_id')

class TravelClassAdmin(admin.ModelAdmin):
    list_display = ('travel_class', )

class TicketAdmin(admin.ModelAdmin):
    list_display = ('reference', 'number_usages', 'reference_type', 'medium')

class RecordIDAdmin(admin.ModelAdmin):
    list_display = ('id', )

class ModeAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_desc', 'long_desc')


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(LatitudeLongitude, LatitudeLongitudeAdmin)
admin.site.register(MonetaryValue, MonetaryValueAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Concession, ConcessionAdmin)
admin.site.register(Usage, UsageAdmin)
admin.site.register(UsageReference, UsageReferenceAdmin)
admin.site.register(UsageFromTo, UsageFromToAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(TravelClass, TravelClassAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(RecordID, RecordIDAdmin)
admin.site.register(Mode, ModeAdmin)



