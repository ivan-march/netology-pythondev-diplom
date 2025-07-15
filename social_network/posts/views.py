from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Like, Post, PostImage
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentSerializer, PostSerializer, PostWriteSerializer


class PostViewSet(ModelViewSet):
    """
    ViewSet для управления постами.
    Позволяет:
    - Получать список и детали поста
    - Создавать, редактировать и удалять свои посты
    - Оставлять комментарии и ставить лайки (только авторизованные пользователи)

    ## Эндпоинты:
    - `GET /posts/` — получить список всех постов
    - `GET /posts/{id}/` — получить детали поста
    - `POST /posts/` — создать пост (только авторизованные)
    - `PUT/PATCH /posts/{id}/` — редактировать пост (только автор)
    - `DELETE /posts/{id}/` — удалить пост (только автор)

    ## Вложенные действия:
    - `POST /posts/{id}/comment/` — оставить комментарий (только авторизованный)
    - `POST /posts/{id}/like/` — поставить или убрать лайк (только авторизованный)
    """
    queryset = Post.objects.prefetch_related('comments', 'likes', 'images').all()
    # queryset = Post.objects.prefetch_related('comments', 'likes').all()  # для одного image
    permission_classes = []

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return PostWriteSerializer
        elif self.action == 'comment':
            return CommentSerializer
        return PostSerializer

    def get_permissions(self):
        """
        Назначает разрешения в зависимости от действия.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=['post'], url_path='comment', permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        """
        Добавляет комментарий к посту.
        Требуется аутентификация.
        """
        post = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='like', permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """
        Ставит или убирает лайк на посте.
        Если пользователь уже лайкнул пост — лайк будет удалён (unlike).
        Иначе — добавлен.
        """
        post = self.get_object()
        user = request.user
        like_obj, created = Like.objects.get_or_create(author=user, post=post)
        if not created:
            like_obj.delete()
            return Response({"status": "unliked"}, status=status.HTTP_200_OK)
        return Response({"status": "liked"}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post', 'delete'], url_path='images', permission_classes=[IsOwnerOrReadOnly])
    def add_images(self, request, pk=None):
        """
        POST: Добавляет новые изображения к посту.
        DELETE: Удаляет все изображения у поста.
        """
        if request.method == 'POST':
            images_data = request.FILES.getlist('images')
            for image in images_data:
                PostImage.objects.create(post=self.get_object(), image=image)
            return Response({"status": "Изображения добавлены"}, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            self.get_object().images.all().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[0-9]+)', permission_classes=[IsOwnerOrReadOnly])
    def delete_image(self, request, pk=None, image_id=None):
        """
        Удаляет конкретное изображение из поста.
        Для поля image модели Post.
        """
        post = self.get_object()
        try:
            image = PostImage.objects.get(post=post, id=image_id)
        except PostImage.DoesNotExist:
            return Response({"detail": "Изображение не найдено"}, status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response({"status": "Изображение удалено"}, status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """
        Возвращает QuerySet постов в зависимости от аутентификации пользователя.
        Аноним: все посты доступны только на чтение.
        Авторизованный: может редактировать/удалять только свои посты.
        """
        user = self.request.user
        if user.is_authenticated:
            return Post.objects.prefetch_related('comments', 'likes')
        return Post.objects.prefetch_related('comments', 'likes').all()
