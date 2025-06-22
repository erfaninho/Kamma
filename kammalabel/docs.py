from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication

APP_INFO = {
    "name":"KammaLabel",
    "version":"1.0.0",
    "description":"Kamma Label Store Website",
    "contac_email":"erfan_bcln@yahoo.com"
}

schema_view = get_schema_view(
    openapi.Info(
        title=APP_INFO["name"],
        default_version=APP_INFO["version"],
        description=APP_INFO["description"],
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email=APP_INFO["contac_email"]),
        license=openapi.License(name="BSD License")
    ),
    public=True,
    authentication_classes=[SessionAuthentication],
    permission_classes=[IsAdminUser]
)

urlpatterns =[
    re_path(r'', schema_view.with_ui('swagger', cache_timeout=0)),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name="schema-json"),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]