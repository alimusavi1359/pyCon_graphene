from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f'{self.username}'


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile', blank=True,
                                null=True, )
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Blog(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان', help_text='عنوان')
    description = models.TextField(null=True, verbose_name='توضیحات')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='blogs', verbose_name='مالک')

    def __str__(self):
        return f'{self.title}'


class Tag(models.Model):
    name = models.CharField(max_length=20, verbose_name='نام')

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    objects = models.Manager()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='posts', verbose_name='بلاگ')
    title = models.CharField(max_length=100, verbose_name='عنوان')
    body = models.TextField(verbose_name='متن')
    image = models.ImageField(null=True, verbose_name='تصویر')
    is_public = models.BooleanField(default=True, verbose_name='عمومی')
    publish_date = models.DateField(null=True, verbose_name='تاریخ انتشار')
    tags = models.ManyToManyField(Tag, related_name='posts', verbose_name='تگ (ها)')

    def __str__(self):
        return f'{self.blog} - {self.title}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='پست')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, related_name='comments',
                             verbose_name='کاربر')
    body = models.TextField(verbose_name='کامنت')

    def __str__(self):
        return f'{self.post} {self.user}'
