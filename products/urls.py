from django.urls import include, path

from rest_framework_nested import routers

from . import views
from utils.default_string import U, T

router = routers.DefaultRouter()
router.register("categories", views.CategoryViewSet, basename=U.V1_CATEGORY)
router.register("products", views.ProductViewSet, basename=U.V1_PRODUCT)

urlpatterns = [
    path("", include(router.urls))
]


