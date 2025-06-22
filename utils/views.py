from rest_framework import status
from rest_framework.response import Response

from .default_string import S


class RetrieveMixin:
    """
        Retrieve a model instance.
    """

    def custom_retrieve(self, status_code=status.HTTP_200_OK, *args, **kwargs):
        kwargs.setdefault(S.CONTEXT, self.get_serializer_context())
        instance = self.get_object()
        serializer = self.get_serializer(instance, context=kwargs[S.CONTEXT])
        return Response(serializer.data)

# Create your views here.
