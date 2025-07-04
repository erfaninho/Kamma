from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.serializers import (UserLoginStartSerializer, UserLoginStepTwoSerializer)

from .models import User, UserRandomNumber

from utils.default_string import T
from utils.views import PostMixin, RetrieveMixin

class UserLoginViewSet(viewsets.GenericViewSet, PostMixin):
    """
        Viewset for user actions
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "login":
            return UserLoginStartSerializer
        if self.action == "verify":
            return UserLoginStepTwoSerializer
        return super().get_serializer_class()
    
    @swagger_auto_schema(
        operation_summary="User Login Start",
        tags=[T.USER_TAG]
    )
    @action(detail=False, methods=["post"])
    def login (self, request, *args, **kwargs):
        return self.custom_create(request, *args, **kwargs)


    @swagger_auto_schema(
        operation_summary="Verify Sent Code",
        tags=[T.USER_TAG]
    )
    @action(detail=False, methods=["post"])
    def verify (self, request, *args, **kwargs):
        self.custom_create(request, *args, **kwargs)