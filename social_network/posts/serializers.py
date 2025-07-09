from rest_framework import serializers
from .models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['author', 'text', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'text', 'image', 'created_at', 'comments', 'likes_count']

    def get_likes_count(self, obj):
        return obj.likes.count()


class PostWriteSerializer(PostSerializer):
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['author']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['author'] = request.user
        else:
            raise serializers.ValidationError({'author': 'Пользователь не авторизован.'})
        return super().create(validated_data)


