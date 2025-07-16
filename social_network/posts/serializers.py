from rest_framework import serializers
from .models import Comment, Post, PostImage


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели `Comment`.
    """
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['author', 'text', 'created_at']


class PostImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели PostImage.
    """
    class Meta:
        model = PostImage
        fields = ['image']


class PostSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для модели `Post`.
    """
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    images = PostImageSerializer(many=True, read_only=True)  # для нескольких image
    location = serializers.SerializerMethodField()

    class Meta:
        model = Post
        # fields = ['id', 'text', 'image', 'created_at', 'comments', 'likes_count']  # для одного image
        fields = [
            'id',
            'text',
            'image',
            'created_at',
            'comments',
            'likes_count',
            'images',
            'location',
            'latitude',
            'longitude'
        ]

    def get_location(self, obj):
        """
        Возвращает локацию через reverse-геокодирование,
        используя широту и долготу.
        """
        if obj.latitude and obj.longitude:
            from geopy.geocoders import Nominatim
            try:
                geolocator = Nominatim(user_agent='post-reverse-geocoder')
                location = geolocator.reverse(f'{obj.latitude}, {obj.longitude}')
                if location:
                    return location.address
            except Exception as e:
                print(f'Ошибка при обратном геокодировании: {e}')
                return None
        return obj.location

    def get_likes_count(self, obj):
        """
        Возвращает количество лайков для текущего поста.
        """
        return obj.likes.count()


class PostWriteSerializer(PostSerializer):
    """
    Сериализатор для создания и обновления постов.
    """
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )  # для нескольких image
    location = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Post
        fields = ['author', 'text', 'images', 'location', 'latitude', 'longitude']
        read_only_fields = ['latitude', 'longitude']

    def validate_location(self, value):
        """
        Валидация поля location.
        """
        if value == '':
            return None
        return value

    def create(self, validated_data):
        """
        Создание нового поста с возможностью загрузки нескольких изображений.
        """
        images_data = validated_data.pop('images', [])
        post = super().create(validated_data)
        for image in images_data:
            PostImage.objects.create(post=post, image=image)
        return post

    def update(self, obj, validated_data):
        """
        Обновление существующего поста.
        """
        obj.location = validated_data.get('location', obj.location)
        obj.text = validated_data.get('text', obj.text)
        images_data = validated_data.pop('images', [])
        if images_data:
            obj.images.all().delete()
            for image in images_data:
                PostImage.objects.create(post=obj, image=image)
        obj.save()
        return obj
