from django.urls import include, path

from rest_framework_nested import routers

from . import views
from utils.default_string import U, T

router = routers.DefaultRouter()
router.register("user", views.UserLoginViewSet, basename=U.V1_USER)

urlpatterns = [
    path("", include(router.urls))
]


