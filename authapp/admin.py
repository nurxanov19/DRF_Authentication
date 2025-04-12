from django.contrib import admin
from django.contrib.auth.models import Group

from .models import CustomUser


admin.site.register(CustomUser)

admin.site.unregister(Group)

# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser
#
# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('phone', 'name', 'is_staff', 'is_superuser')
#     search_fields = ('phone', 'name')
#     ordering = ('phone',)
#
#     fieldsets = (
#         (None, {'fields': ('phone', 'password')}),
#         ('Personal info', {'fields': ('name',)}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login',)}),
#     )
#
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('phone', 'name', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')}
#         ),
#     )

