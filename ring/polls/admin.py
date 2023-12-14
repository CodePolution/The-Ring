from django.contrib import admin
from .models import ChainStatus

@admin.register(ChainStatus)
class LikesAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status']
