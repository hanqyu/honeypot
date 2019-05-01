from django.conf.urls import url
from django.urls import path
from . import api, views
from django.urls import include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from rest_framework_simplejwt import views as jwt_views


router = routers.DefaultRouter()
router.register('user', api.UserViewSet)
router.register('region', api.RegionViewSet)
router.register('district', api.DistrictViewSet)
router.register('question', api.QuestionViewSet)
router.register('answer', api.AnswerViewSet)
router.register('create_user', api.CreateUserSerializer)
router.register('login_user', api.CreateUserSerializer)


urlpatterns = [
    url(r'^doc', get_swagger_view(title='Rest API Document')),
    url(r'^v1/', include((router.urls, 'user'), namespace='user')),
    url(r'^v1/', include((router.urls, 'region'), namespace='region')),
    url(r'^v1/', include((router.urls, 'district'), namespace='district')),
    url(r'^v1/', include((router.urls, 'question'), namespace='question')),
    url(r'^v1/', include((router.urls, 'answer'), namespace='answer')),
    url(r'^v1/', include((router.urls, 'create_user'), namespace='create_user')),
    url(r'^v1/', include((router.urls, 'login_user'), namespace='login_user')),
]

urlpatterns += [
    url('recent/', views.recent_question, name='recent'),
]


urlpatterns += [
    url(r'^token/$', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^token/refresh/$', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
