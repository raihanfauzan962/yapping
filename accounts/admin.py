from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    # Use the custom forms for creating and changing users
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    # List of fields to display in the list view
    list_display = ["email", "username", "is_superuser"]

    # Customize fieldsets and add_fieldsets to remove redundant fields
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'email', 'password1', 'password2')}),
    )

    # Adjust search and filter options
    search_fields = ['email', 'username']
    list_filter = ('is_superuser', 'is_staff', 'is_active')

# Register the custom user admin
admin.site.register(CustomUser, CustomUserAdmin)
