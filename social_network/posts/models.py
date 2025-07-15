from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Post(models.Model):
    """
    Модель поста пользователя.

    ## Поля:
    - `author`: Автор поста (ForeignKey на CustomUser)
    - `text`: Текст поста
    - `image`: Изображение, загружаемое пользователем
    - `created_at`: Дата и время публикации
    - `location`: Адрес, указанный пользователем
    - `latitude`: Широта
    - `longitude`: Долгота
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name=_('Автор'))
    text = models.TextField(verbose_name=_('Текст'))
    image = models.ImageField(upload_to='posts', verbose_name=_('Изображение'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата публикации'))
    location = models.CharField(max_length=255, verbose_name=_('Адрес'), blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('Широта'), blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('Долгота'), blank=True, null=True)

    class Meta:
        verbose_name = _('Пост')
        verbose_name_plural = _('Посты')

    def __str__(self):
        return f'{self.author} - {self.created_at}'
    
    def save(self, *args, **kwargs):
        """
        При сохранение поста проверяет изменение location.
        Если да, то выполнит запрос в geopy и обновит
        latitude и longitude.
        """
        if self.location:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="post-geocoder")
            try:
                location_data = geolocator.geocode(self.location)
                if location_data:
                    self.latitude = location_data.latitude
                    self.longitude = location_data.longitude
                    super().save(update_fields=['latitude', 'longitude'])
            except Exception as e:
                print(f"Ошибка при геокодировании: {e}")
        elif self.longitude and self.latitude and not self.location:
            self.latitude = None
            self.longitude = None

        super().save(*args, **kwargs)



class PostImage(models.Model):
    """
    Модель для хранения изображений, связанных с постом.

    ## Поля:
    - `post`: Пост, к которому привязано изображение
    - `image`: Изображение, загружаемое пользователем
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', verbose_name=_('Пост'))
    image = models.ImageField(upload_to='posts/images', verbose_name=_('Изображение'))

    class Meta:
        verbose_name = _('Изображение поста')
        verbose_name_plural = _('Изображения постов')

    def __str__(self):
        return f'Изображения для {self.post}'


class Like(models.Model):
    """
    Модель "лайка" к посту.

    ## Поля:
    - `author`: Кто поставил лайк
    - `post`: Какой пост был оценён

    ## Ограничения:
    - Один пользователь может лайкнуть один пост только один раз
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name=_('Автор'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name=_('Пост'))

    class Meta:
        verbose_name = _('Лайк')
        verbose_name_plural = _('Лайки')
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'post'],
                name='unique_like'
            )
        ]

    def __str__(self):
        return f'{self.author}: {self.post}'


class Comment(models.Model):
    """
    Комментарий к посту.

    ## Поля:
    - `author`: Автор комментария
    - `post`: Пост, к которому относится комментарий
    - `text`: Текст комментария
    - `created_at`: Дата и время создания комментария
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Автор'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Пост'))
    text = models.TextField(verbose_name=_('Текст'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата публикации'))

    class Meta:
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')

    def __str__(self):
        return f'{self.author}: {self.post}'
