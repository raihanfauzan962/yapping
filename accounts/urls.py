from django.urls import path
from .views import profile_view

urlpatterns = [
    path('profile/', profile_view, name='account_profile'),  # Matches Allauth expectations
]
