from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name=_('Автор'))
    text = models.TextField(verbose_name=_('Текст'))
    image = models.ImageField(upload_to='posts', verbose_name=_('Изображение'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата публикации'))

    class Meta:
        verbose_name = _('Пост')
        verbose_name_plural = _('Посты')

    def __str__(self):
        return f'{self.author} - {self.created_at}'


# для доп. задания
# class PostImage(models.Model):
#     ...


class Like(models.Model):
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
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Автор'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Пост'))
    text = models.TextField(verbose_name=_('Текст'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата публикации'))

    class Meta:
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')

    def __str__(self):
        return f'{self.author}: {self.post}'
