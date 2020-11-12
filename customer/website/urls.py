from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.customer_login, name='login'),
    path('logout/', views.customer_logout, name='logout'),
    path('connect/', views.connect, name='connect'),
    path('purchases/', views.purchases, name='purchases'),
    path('concessions/', views.concessions, name='concessions'),
    path('usage/', views.usage, name='usage'),
]
