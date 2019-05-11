from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient, RequestsClient
from django.contrib.auth import get_user_model
import json, requests
from api.tokens import TokenSerializer

User = get_user_model()


class Test:
    client = APIClient()
    factory = APIRequestFactory()
    admin_user = User.objects.first()
    token = TokenSerializer(admin_user).token
    refresh_token, access_token = token['refresh'], token['access']
    password = '123456'
    url = 'http://testserver'
    data = {'content-type': 'application/json'}
    client.credentials(HTTP_AUTHORIZATION='Token '+ access_token)

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
    api_url = '/api/v1/auth/register/'

    def __init__(self, fail_test=None):
        super(RegisterTest, self).__init__()
        self.fail_test = fail_test
        self.url += self.api_url

    def test(self, ver):
        if self.fail_test is 'duplicate_email':
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

        request = self.factory.post(self.api_url, json.dumps(self.data), content_type='application/json')
        response = view(request)
        assert response.status_code == 200
        return response

    def test_client(self):
        self.recount_test_user()
        return requests.post(self.url, data=self.data)

    def duplicate_email(self):
        self.set_data(username=self.admin_user.username, email=self.admin_user.email, password=self.admin_user.password)


class UserTest(Test):
    api_url = '/api/v1/user/'

    def __init__(self, id=1):
        super(UserTest, self).__init__()
        self.url += self.api_url
        self.data['id'] = id
        print('check: data must be dictionary, ignore if it is')

    def test_client(self):
        return self.client.get(self.url, data=self.data)

    def test_get_user(self):
        return self.client.get(self.url)



response = RegisterTest(fail='duplicate_email').test(ver='client')

TokenSerializer(token=Test().token)

ut = UserTest()
ut.test_client()
ut.test_get_user()




