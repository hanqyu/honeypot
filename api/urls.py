from django.conf.urls import url
from django.urls import path
from .views import (
    UserViewSet,
    RegionViewSet,
    DistrictViewSet,
    QuestionViewSet,
    AnswerViewSet,
    CategoryViewSet,
    RegistrationAPI,
    QuestionAPI,
    LoginAPI,
    UserAPI,
    AnswerAPI,
    SelectAnswerAPI,
    RecentQuestionAPI,
)
from django.urls import include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = routers.DefaultRouter()
router.register('user', UserViewSet)
router.register('region', RegionViewSet)
router.register('district', DistrictViewSet)
router.register('question', QuestionViewSet)
router.register('answer', AnswerViewSet)
router.register('category', CategoryViewSet)

urlpatterns = [
    url(r'^doc', get_swagger_view(title='Rest API Document')),
    url(r'^v1/view/', include((router.urls, 'user'), namespace='user')),
    url(r'^v1/view/', include((router.urls, 'region'), namespace='region')),
    url(r'^v1/view/', include((router.urls, 'district'), namespace='district')),
    url(r'^v1/view/', include((router.urls, 'question'), namespace='question')),
    url(r'^v1/view/', include((router.urls, 'answer'), namespace='answer')),
    url(r'^v1/view/', include((router.urls, 'category'), namespace='category')),
]

urlpatterns += [
    url(r'^v1/auth/register/$', RegistrationAPI.as_view()),
    url(r'^v1/auth/login/$', LoginAPI.as_view()),
    url(r'^v1/auth/user/$', UserAPI.as_view()),
    url(r'^v1/question/$', QuestionAPI.as_view()),
    url(r'^v1/question/(?P<pk>\d+)/$', QuestionAPI.as_view()),
    url(r'^v1/answer/$', AnswerAPI.as_view()),
    url(r'^v1/answer/(?P<pk>\d+)/select/$', SelectAnswerAPI.as_view()),
    url(r'^v1/question/recent/$', RecentQuestionAPI.as_view())
]


urlpatterns += [
    url(r'^token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
]
