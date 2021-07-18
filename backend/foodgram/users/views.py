from djoser.views import UserViewSet


from .serializers import UserCreateSerializer


class CustomUserViewSet(UserViewSet):
    serializer_class = UserCreateSerializer
