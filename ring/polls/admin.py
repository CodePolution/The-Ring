from django.contrib import admin
from .models import ChainStatus, Submit, Task


@admin.register(ChainStatus)
class LikesAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status']


@admin.register(Submit)
class LikesAdmin(admin.ModelAdmin):
    list_display = ['one', 'two', 'three', 'four']


admin.site.register(Task)