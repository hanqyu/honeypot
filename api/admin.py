from django.contrib import admin
from rangefilter.filter import DateTimeRangeFilter, DateRangeFilter
from .models import *
from django.http import HttpResponseRedirect


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'last_login', 'created_at', 'region', 'avatar')
    list_filter = ('region',
                   ('created_at', DateRangeFilter),
                   ('last_login', DateRangeFilter),
                   )
    search_fields = ('id', 'email', 'username')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'region', 'anonymous', 'text', 'used_voting', 'category', 'selected_answer',
                    'has_selected_answer', 'updated_at', 'created_at')
    list_filter = ('category',
                   'region',
                   ('created_at', DateRangeFilter)
                   )
    search_fields = ('id', 'user', 'text')


admin.site.register(User, UserAdmin)
admin.site.register(Region)
admin.site.register(District)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Category)


class AuthRequiredMiddleware(object):
    def process_request(self, request):
        redirect_url = '/admin/login'

        if not request.user.is_authenticated() and request.path != redirect_url:
            return HttpResponseRedirect(redirect_url)
        return None
