from django.urls import include, path
from rest_framework import routers

from api.views import UserViewSet, IngredientViewSet, TagViewSet


app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    # path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
