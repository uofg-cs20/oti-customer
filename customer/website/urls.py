from django.urls import include, path
from . import views
from rest_framework import routers

app_name = 'website'

# Set up the router for the API URLs
router = routers.DefaultRouter()
router.register(r'purchases', views.PurchaseViewSet)
router.register(r'concessions', views.ConcessionViewSet)
router.register(r'usages', views.UsageViewSet)

urlpatterns = [
    #path('', views.index, name='index'),
    #path('register/', views.register, name='register'),
    path('api/', include(router.urls)),
    path('', views.customer_login, name='login'),
    path('logout/', views.customer_logout, name='logout'),
    path('connect/', views.connect, name='connect'),
    path('purchases/', views.purchases, name='purchases'),
    path('concessions/', views.concessions, name='concessions'),
    path('usage/', views.usage, name='usage'),
    #path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
