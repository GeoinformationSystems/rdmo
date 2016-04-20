from rest_framework.serializers import ModelSerializer

from .models import *


class ValueSerializer(ModelSerializer):

    class Meta:
        model = Value
        fields = ('id', 'index', 'created', 'updated', 'text', 'snapshot', 'attribute', 'valueset')


class ValueSetSerializer(ModelSerializer):

    class Meta:
        model = ValueSet
        fields = ('id', 'index', 'created', 'updated', 'snapshot', 'attributeset')