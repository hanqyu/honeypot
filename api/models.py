from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

# from django.api.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, default='avatars/defaut.jpg')
    bio = models.CharField(max_length=50, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    region = models.ForeignKey('Region', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager.UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # def __init__(self):
    #     self._avatar_url = self.get_avatar_url()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        managed = True
    #
    # def get_avatar_url(self):
    #     try:
    #         return self.avatar.url
    #     except AttributeError:
    #         return None

    # def email_user(self, subject, message, from_email=None, **kwargs):
    #     '''
    #     Sends an email to this User.
    #     '''
    #     send_mail(subject, message, from_email, [self.email], **kwargs)


class Question(models.Model):
    '''
    :param region: option.
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='question')
    region = models.ForeignKey('Region', on_delete=models.SET_NULL, null=True, related_name='question')
    anonymous = models.BooleanField(default=True)
    text = models.CharField(max_length=1000)
    used_voting = models.IntegerField(default=0, validators=(MinValueValidator(0),))
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='question')
    selected_answer = models.ForeignKey('Answer', on_delete=models.SET_NULL, default=None, null=True, related_name='question_selected_to')
    has_selected_answer = models.BooleanField(default=False)
    answer_count = models.IntegerField(default=0)
    # image = models.ImageField(upload_to='question_images/')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True

'''
class QuestionVote(models.Model):
    question = models.ForeignKey('Question', on_delete=)
'''
# Answer.objects.filter(pk=1).first()._do_update()

class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answer')
    question = models.ForeignKey('Question', on_delete=models.SET_NULL, null=True, related_name='answer')
    anonymous = models.BooleanField(default=True)
    text = models.CharField(max_length=3000)
    is_selected = models.BooleanField(default=False)
    # image = models.ImageField(upload_to='answer_images/')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True


class Category(models.Model):
    name = models.CharField(max_length=30)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True


class Tag(models.Model):
    name = models.CharField(max_length=20)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True

'''
class QuestionTag(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        managed = True
'''


class District(models.Model):
    name = models.CharField(max_length=20)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True


class Region(models.Model):
    name = models.CharField(max_length=20)
    district = models.ForeignKey('District', on_delete=models.PROTECT, null=True, related_name='region')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
