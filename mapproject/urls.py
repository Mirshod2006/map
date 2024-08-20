from django.contrib import admin
from django.urls import path
from . import views




urlpatterns = [
    path('', views.my_view, name='my_view'),
    path('get_data/', views.get_data, name='get_data'),
    path('get_meteoData/', views.get_meteoData, name='get_meteoData'),
    path('BaseUpdate/', views.BaseUpdate, name='BaseUpdate'),
    path('admin/', admin.site.urls),
]