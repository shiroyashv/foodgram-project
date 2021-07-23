from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from recipes.models import Follow

from .models import CustomUser


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = '__all__'


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Follow.objects.filter(user=request.user, author=obj).exists()
