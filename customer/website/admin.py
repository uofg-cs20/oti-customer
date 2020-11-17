from django.contrib import admin

from .models import *

class AccountAdmin(admin.ModelAdmin):
    list_display = ('customer', 'operator_id')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id',)

class MonetaryValueAdmin(admin.ModelAdmin):
    list_display = ('amount', 'currency')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'payment_type', 'payment_method', 'price')

class DiscountAdmin(admin.ModelAdmin):
    list_display = ('discount_type', 'discount_value', 'discount_description')

class ConcessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount', 'transaction', 'valid_from_date_time', 'valid_to_date_time', 'conditions', 'customer')

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(MonetaryValue, MonetaryValueAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Concession, ConcessionAdmin)