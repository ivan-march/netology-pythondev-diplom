from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Like, Post
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentSerializer, PostSerializer, PostWriteSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.prefetch_related('comments', 'likes').all()
    permission_classes = []

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostWriteSerializer
        elif self.action == 'comment':
            return CommentSerializer
        return PostSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=['post'], url_path='comment', permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, post=post)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='like', permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        like_obj, created = Like.objects.get_or_create(author=user, post=post)

        if not created:
            like_obj.delete()
            return Response({"status": "unliked"}, status=status.HTTP_200_OK)

        return Response({"status": "liked"}, status=status.HTTP_200_OK)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Post.objects.prefetch_related('comments', 'likes')
        return Post.objects.prefetch_related('comments', 'likes').all()
