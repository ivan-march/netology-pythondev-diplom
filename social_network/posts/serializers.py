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
                geolocator = Nominatim(user_agent="post-reverse-geocoder")
                location = geolocator.reverse(f"{obj.latitude}, {obj.longitude}")
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

    class Meta:
        model = Post
        fields = ['author', 'text', 'images', 'location', 'latitude', 'longitude']

    def create(self, validated_data):
        """
        Создание нового поста с возможностью загрузки нескольких изображений.
        """
        images_data = validated_data.pop('images', [])
        post = super().create(validated_data)
        for image in images_data:
            PostImage.objects.create(post=post, image=image)
        return post

    # def update(self, obj, validated_data):
    #     """
    #     Обновление существующего поста с возможностью добавления/обновления изображений.
    #     """
    #     print(validated_data)

    #     new_location = validated_data.get('location', None)
    #     if new_location:
    #         from geopy.geocoders import Nominatim
    #         try:
    #             geolocator = Nominatim(user_agent="post-geocoder")
    #             location_data = geolocator.geocode(new_location)
    #             if location_data:
    #                 validated_data['latitude'] = location_data.latitude
    #                 validated_data['longitude'] = location_data.longitude
    #         except Exception as e:
    #             print(f"Ошибка геокодирования: {e}")
    #             raise serializers.ValidationError({"location": "Не удалось получить координаты"})
    #         # Добавляем новое значение location в validated_data
    #     if 'location' in validated_data:
    #         print(validated_data['location'])
    #         validated_data['location'] = new_location  # Теперь DRF сохранит его корректно
    #     images_data = validated_data.pop('images', [])
    #     if images_data:
    #         obj.images.all().delete()
    #         for image in images_data:
    #             PostImage.objects.create(post=obj, image=image)
        
    #     return super().update(obj, validated_data)


    def update(self, instance, validated_data):
        # Просто передаём данные дальше — всё остальное делает метод save()
        images_data = validated_data.pop('images', [])
        
        # Обновляем поля поста
        instance.location = validated_data.get('location', instance.location)
        instance.text = validated_data.get('text', instance.text)

        # Обрабатываем изображения
        if images_data:
            instance.images.all().delete()
            for image in images_data:
                PostImage.objects.create(post=instance, image=image)

        # Сохраняем пост → вызывается Post.save(), где происходит геокодирование
        instance.save()

        return instance