from .models import Purchase

# Given a User object, return that user's Purchase instances
def getPurchases(user):
    return Purchase.objects.filter(customer_id=user.id)
