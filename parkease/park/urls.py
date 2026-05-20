from django.urls import path
from . import views

app_name = 'park'

urlpatterns = [
    path('', views.index, name='index'),
    path('booking/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('booking/<int:booking_id>/pay/', views.make_payment, name='make_payment'),
]
