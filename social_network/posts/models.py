from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Post(models.Model):
    ...


# для доп. задания
# class PostImage(models.Model):
#     ...


class Like(models.Model):
    ...


class Comment(models.Model):
    ...
