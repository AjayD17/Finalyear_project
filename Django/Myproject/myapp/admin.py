from django.contrib import admin
from .models import Albumin, CustomUser, Profile

admin.site.register(Albumin)
admin.site.register(Profile)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number')
