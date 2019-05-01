from django.conf.urls import url
from django.urls import path
from . import views
from django.urls import include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from rest_framework_simplejwt import views as jwt_views


router = routers.DefaultRouter()
router.register('user', views.UserViewSet)
router.register('region', views.RegionViewSet)
router.register('district', views.DistrictViewSet)
router.register('question', views.QuestionViewSet)
router.register('answer', views.AnswerViewSet)
# router.register('create_user', views.CreateUserSerializer)
# router.register('login_user', views.LoginUserSerializer)


urlpatterns = [
    url(r'^doc', get_swagger_view(title='Rest API Document')),
    url(r'^v1/', include((router.urls, 'user'), namespace='user')),
    url(r'^v1/', include((router.urls, 'region'), namespace='region')),
    url(r'^v1/', include((router.urls, 'district'), namespace='district')),
    url(r'^v1/', include((router.urls, 'question'), namespace='question')),
    url(r'^v1/', include((router.urls, 'answer'), namespace='answer')),
    # url(r'^v1/', include((router.urls, 'create_user'), namespace='create_user')),
    # url(r'^v1/', include((router.urls, 'login_user'), namespace='login_user')),
]


urlpatterns += [
    url(r'^token/$', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^token/refresh/$', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
