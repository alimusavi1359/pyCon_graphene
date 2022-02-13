import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from graphene import relay
from graphene_django import DjangoObjectType
from django.contrib.auth import authenticate
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.shortcuts import get_token

import blog.views
from blog.models import User, Profile, Blog, Tag, Post, Comment
import graphql_jwt


class UserType(DjangoObjectType):
    class Meta:
        model = User
        # fields = ("id", "name", "ingredients")


class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        # fields = ("id", "user", "first_name", "last_name")


class PostType(DjangoObjectType):
    class Meta:
        model = Post


class BlogType(DjangoObjectType):
    posts = graphene.List(PostType)

    class Meta:
        model = Blog
        # fields = ('title', )

    def resolve_posts(self, info):
        user: get_user_model() = info.context.user
        return blog.views.get_all_posts(user)


class TagType(DjangoObjectType):
    id = graphene.ID(source='pk', required=True)

    class Meta:
        model = Tag


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment


class PostNode(DjangoObjectType):
    id = graphene.ID(source='pk', required=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'tags', 'is_public']
        filter_fields = {
            'title': ['exact', 'icontains', 'istartswith'],
            'tags__id': ['in'],

        }
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    users = graphene.List(UserType)
    blogs = graphene.List(BlogType)
    posts = graphene.List(PostType)
    # posts = DjangoFilterConnectionField(PostNode)
    tags = graphene.List(TagType)
    tag_by_name = graphene.List(TagType, name=graphene.String(required=True))

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')

        return user

    def resolve_users(self, info):
        return get_user_model().objects.all()

    def resolve_blogs(self, info):
        return Blog.objects.all()

    def resolve_posts(self, info, **kwargs):
        user: get_user_model() = info.context.user
        return blog.views.get_all_posts(user)

    def resolve_tags(self, info):
        return Tag.objects.all()

    def resolve_tag_by_name(self, info, name):
        return Tag.objects.filter(name__icontains=name)
