from typing import List

from rest_framework import serializers, exceptions
from rest_framework.reverse import reverse


class BaseSerializer(serializers.Serializer):
    """
        Base Serializer
    """

    def update(self, instance, validated_data):
        """
            Update
        """
        pass

    def create(self, validated_data):
        """
            Create
        """
        pass