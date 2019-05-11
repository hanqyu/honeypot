from django.contrib import admin
from rangefilter.filter import DateTimeRangeFilter, DateRangeFilter
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'username', 'last_login', 'created_at', 'region']
    list_filter = ('region',
        ('created_at', DateRangeFilter),
        ('last_login', DateRangeFilter),
    )
    search_fields = ['id', 'email', 'username']


admin.site.register(User, UserAdmin)
admin.site.register(Region)
admin.site.register(District)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Category)
