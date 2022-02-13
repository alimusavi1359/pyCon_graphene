import graphene

from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from graphql_jwt.exceptions import PermissionDenied

import blog
from api.schema.query import UserType, BlogType, PostType
from blog import views
from blog.models import Post, Blog, Tag


class Login(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user, token = blog.views.login(username, password)
        return Login(user=user, token=token)


class CreatePostInput(graphene.InputObjectType):
    blog_id = graphene.Int(required=True)
    title = graphene.String(required=True)
    body = graphene.String(required=True)
    image = Upload(required=False)
    is_public = graphene.Boolean(required=False)
    publish_date = graphene.Date()


class CreatePost(graphene.Mutation):
    Output = PostType

    class Arguments:
        input_data = CreatePostInput(required=True, name="input")

    def mutate(self, info, input_data: CreatePostInput):
        current_user = info.context.user
        try:
            blog: Blog = Blog.objects.get(id=input_data.blog_id)
        except Blog.DoesNotExist:
            raise Exception("selected blog dose not exist.")

        if blog.owner.user != current_user:
            raise PermissionDenied()

        post: Post = Post()
        post.blog_id = input_data.blog_id
        post.title = input_data.title
        post.body = input_data.body
        post.is_public = input_data.is_public
        post.publish_date = input_data.publish_date
        post.image = input_data.image
        post.save()

        return post


class TagPost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        post_id = graphene.Int(required=True)
        tags_id = graphene.List(graphene.Int)

    @login_required
    def mutate(self, info, post_id, tags_id):
        post = views.tag_post(post_id=post_id, tags_id=tags_id)
        return TagPost(post)


class DeleteTagPost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        post_id = graphene.Int(required=True)
        tags_id = graphene.List(graphene.Int)

    # @login_required
    def mutate(self, info, post_id, tags_id):
        post = views.delete_tag_post(post_id=post_id, tags_id=tags_id)
        return TagPost(post)


class Mutation(graphene.ObjectType):
    login = Login.Field()
    create_post = CreatePost.Field()
    tag_post = TagPost.Field()
    delete_tag_post = DeleteTagPost.Field()
