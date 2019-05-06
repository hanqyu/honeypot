from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient, RequestsClient
from django.contrib.auth import get_user_model
import json, requests
from rest_framework.authtoken.models import Token


class Test:
    client = APIClient()
    factory = APIRequestFactory()
    admin_user = User.objects.first()
    token = Token(admin_user).get_tokens_for_user()
    refresh_token, access_token = token['refresh'], token['access']
    password = '123456'

    def __init__(self):
        self.create_last_test_user()
        self.reset_data()

    def create_last_test_user(self):
        last_test_user = User.objects.filter(email__contains='test').last()
        self.username, self.email = self.increment_test_user(last_test_user.username, last_test_user.email)

    def recount_test_user(self):
        self.create_last_test_user()

    def set_data(self, username, email, password):
        self.data = {
            'username': username,
            'email': email,
            'password': password
        }

    def reset_data(self):
        self.set_data(username=self.username, email=self.email, password=self.password)

    @staticmethod
    def increment_test_user(username, email):
        import re

        next_username = 'test%d' % (int(re.findall('\d+', username)[0]) + 1)
        next_email = 'test%d@test.com' % (int(re.findall('\d+', email)[0]) + 1)
        return next_username, next_email


class RegisterTest(Test):
    factory_url = '/api/v1/auth/register/'

    def __init__(self, fail=None):
        super(RegisterTest, self).__init__()
        self.fail = fail

    def test(self, ver):
        if self.fail is 'duplicate_email':
            self.duplicate_email()

        if ver is 'factory':
            response = self.test_factory()
        elif ver is 'client':
            response = self.test_client()

        print('''Status Code: %d\nContent: %s''' % (response.status_code, response.content))
        return response

    def test_factory(self):
        from api.views import RegistrationAPI
        self.recount_test_user()
        view = RegistrationAPI().as_view()

        request = self.factory.post(self.factory_url, json.dumps(self.data), content_type='application/json')
        response = view(request)
        assert response.status_code == 200
        return response

    def test_client(self):
        url = 'http://localhost:8000' + self.factory_url
        self.recount_test_user()
        return requests.post(url, data=self.data)

    def duplicate_email(self):
        self.set_data(username=self.admin_user.username, email=self.admin_user.email, password=self.admin_user.password)


response = RegisterTest(fail='duplicate_email').test(ver='client')