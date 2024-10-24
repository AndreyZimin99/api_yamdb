from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'is_staff',
    )

    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')

    list_editable = ('role', 'is_active')

    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Personal info',
            {'fields': ('first_name', 'last_name', 'email', 'bio')},
        ),
        (
            'Permissions',
            {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')},
        ),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'role',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
    )

    ordering = ('username',)


admin.site.register(User, UserAdmin)
