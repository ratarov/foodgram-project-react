# from api.views import (APISignup, APIToken, CategoryViewSet, CommentViewSet,
#                        GenreViewSet, ReviewViewSet, TitleViewSet, UsersViewSet)
from django.urls import include, path
from rest_framework import routers

app_name = 'api'

router = routers.DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
]
