from django.contrib import admin

from .models import CustomUser, UserData


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'account_type',
        'mobile',
        'email',
        'is_account_active',
        'is_active',
        'is_superuser',
        'created',
        'modified',
    )
    list_filter = (
        'created',
        'is_account_active',
        'account_type',
    )


@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'name',
        'gender',
        'date_of_birth',
        'company_name',
        'created',
        'modified',
    )
    list_filter = ('user', 'date_of_birth', 'created', 'modified')
    search_fields = ['name']
