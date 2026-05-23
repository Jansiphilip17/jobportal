from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, EmailVerificationToken, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model in the list view
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'date_joined')
    list_filter  = ('role', 'is_verified', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    # IMPORTANT: our model uses email as USERNAME_FIELD, not username
    # So we must override both fieldsets and add_fieldsets
    fieldsets = (
        (None,            {'fields': ('email', 'password')}),
        (_('Personal'),   {'fields': ('first_name', 'last_name', 'phone', 'profile_photo')}),
        (_('Role'),       {'fields': ('role',)}),
        (_('Permissions'),{'fields': ('is_active', 'is_staff', 'is_superuser',
                                      'is_verified', 'groups', 'user_permissions')}),
        (_('Dates'),      {'fields': ('date_joined', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role',
                       'password1', 'password2', 'is_active', 'is_staff', 'is_verified'),
        }),
    )

    # Required: tell Django admin which field is the username
    # (replaces the default 'username' field)
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display  = ('user', 'created_at', 'expires_at', 'is_used')
    list_filter   = ('is_used',)
    search_fields = ('user__email',)
    readonly_fields = ('created_at',)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display  = ('user', 'created_at', 'expires_at', 'is_used')
    list_filter   = ('is_used',)
    search_fields = ('user__email',)
    readonly_fields = ('created_at',)