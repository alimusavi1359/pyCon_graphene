from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from graphql_jwt.exceptions import PermissionDenied
from graphql_jwt.shortcuts import get_token

from blog.models import Profile, Post, Tag


def get_all_posts(user: get_user_model()):
    posts = Post.objects.all()
    if user.is_superuser:
        return posts
    elif user.is_anonymous:
        return posts.filter(is_public=True)
    elif user.is_authenticated:
        profile: Profile = user.profile
        return posts.filter(Q(is_public=True) | Q(blog__owner=profile))


def tag_post(post_id, tags_id):
    post = Post.objects.get(id=post_id)
    for t in tags_id:
        try:
            tag = Tag.objects.get(id=t)
            post.tags.add(tag)
        except Tag.DoesNotExist:
            pass

    post.save()
    return post


def delete_tag_post(post_id, tags_id):
    post = Post.objects.get(id=post_id)
    for t in tags_id:
        try:
            tag = Tag.objects.get(id=t)
            post.tags.remove(tag)
        except Tag.DoesNotExist:
            pass

    post.save()
    return post


def login(username, password):
    user = authenticate(username=username, password=password)
    if user is None:
        raise PermissionDenied()
    else:
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        token = get_token(user)
        return user, token
