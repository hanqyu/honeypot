from django.contrib import admin
from rangefilter.filter import DateTimeRangeFilter, DateRangeFilter
from .models import *
from django.http import HttpResponseRedirect


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'username', 'last_login', 'created_at', 'region', 'avatar', 'bio']
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


class AuthRequiredMiddleware(object):
    def process_request(self, request):
        redirect_url = '/admin/login'

        if not request.user.is_authenticated() and request.path != redirect_url:
            return HttpResponseRedirect(redirect_url)
        return None
