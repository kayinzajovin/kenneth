from django.urls import path
from . import views

app_name = 'park'

urlpatterns = [
    path('', views.index, name='index'),
    path('booking/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('booking/<int:booking_id>/pay/', views.make_payment, name='make_payment'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/driver/', views.driver_dashboard, name='driver_dashboard'),
    path('dashboard/attendant/', views.attendant_dashboard, name='attendant_dashboard'),
]
