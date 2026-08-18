from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 1. Njia ya kuingia kwenye Admin Panel ya Django
    path('admin/', admin.site.urls),

    # 2. Inajumuisha URL zote kutoka app ya 'pharmacy' moja kwa moja
    path('', include('pharmacy.urls')), 
]