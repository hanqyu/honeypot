from django import forms
from .models import *


# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name', 'email')
#         # user, name, email, bio, region_id, created_at,

# class PostUrlForm(forms.Form):
#     class Meta:
#         fields = forms.URLField(help_text='올바른 url 주소를 입력하세요')