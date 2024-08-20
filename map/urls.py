from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('mapproject.urls')),
    # path('register/', include('register.urls')),
    # path('login/', include('login.urls')),
    path('admin/', admin.site.urls),
]
