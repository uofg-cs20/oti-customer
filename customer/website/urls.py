from django.urls import include, path
from django.conf.urls import url
from . import views
from rest_framework import routers

app_name = 'website'

# Set up the router for the API URLs
router = routers.DefaultRouter()
router.register(r'purchase', views.PurchaseViewSet)
router.register(r'concession', views.ConcessionViewSet)
router.register(r'usage', views.UsageViewSet)

urlpatterns = [
    #path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('api/', include(router.urls)),
    path('', views.customer_login, name='login'),
    path('logout/', views.customer_logout, name='logout'),
    path('connect/', views.connect, name='connect'),
    path('purchases/', views.purchases, name='purchases'),
    path('concessions/', views.concessions, name='concessions'),
    path('usage/', views.usage, name='usage'),
    url(r'^delete/(?P<pk>[0-9]+)/$', views.disconnect, name='disconnect')
    #path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
