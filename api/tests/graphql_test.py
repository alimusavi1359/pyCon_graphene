import json

from django.core.files.uploadedfile import SimpleUploadedFile
from graphene_django.utils.testing import GraphQLTestCase
from graphene_file_upload.django.testing import GraphQLFileUploadTestCase

from blog import models


class GraphqlTestCase(GraphQLTestCase):
    GRAPHQL_URL = '/api/graphql'

    token = ''

    @classmethod
    def setUpTestData(self):
        tag_django = models.Tag.objects.create(name='Django')
        tag_python = models.Tag.objects.create(name='python')
        tag_pycon = models.Tag.objects.create(name='pycon')
        tag_iran = models.Tag.objects.create(name='iran')

        ali = models.User.objects.create_user(username='ali', password='ali123')
        ali_profile = models.Profile.objects.create(user=ali, first_name='ali')
        ali_blog = models.Blog.objects.create(title="ali's blog", owner=ali_profile, description='taking about Django')

        ali_post1 = models.Post.objects.create(blog=ali_blog, title='my first post', body='my first post my first post')

        ali_post2 = models.Post.objects.create(blog=ali_blog, title='first post about django', body='django is easy')
        ali_post2.tags.add(tag_django)
        ali_post2.save()
        ali_comment_post2 = models.Comment.objects.create(post=ali_post2, user=ali_profile, body="my first comment")

        ali_post3 = models.Post.objects.create(blog=ali_blog, title='django private post', body='this post not public.',
                                               is_public=False)
        ali_post3.tags.add(tag_django)
        ali_post3.tags.add(tag_pycon)
        ali_post3.save()

    def take_token(self):
        response = self.query(
            '''
                mutation {
                  login(username: "ali", password: "ali123") {
                    token
                  }
                }

            '''
        )
        content = json.loads(response.content)
        token = content['data']['login']['token']
        return token

    def test_login(self):
        response = self.query(
            '''
                mutation {
                  login(username: "ali", password: "ali123") {
                    token
                    user{
                      id
                      username
                    }
                  }
                }

            '''
        )
        content = json.loads(response.content)
        self.token = content['data']['login']['token']
        username = content['data']['login']['user']['username']
        self.assertIsNotNone(self.token)
        self.assertEqual(username, 'ali')
        self.assertResponseNoErrors(response)

    def test_login_error(self):
        response = self.query(
            '''
                mutation {
                  login(username: "ali", password: "1111") {
                    token
                    user{
                      id
                      username
                    }
                  }
                }

            '''
        )
        content = json.loads(response.content)
        errorrs = content['errors']
        error_msg = content['errors'][0]['message']

        self.assertEqual(len(errorrs), 1)
        self.assertEqual(error_msg, 'You do not have permission to perform this action')

    def test_me(self):
        token = self.take_token()
        response = self.query(
            '''
            {
              me {
                id
                username
              }
            }
            ''',
            headers=
            {
                "HTTP_AUTHORIZATION": "jwt " + token
            }
        )

        content = json.loads(response.content)
        id = content['data']['me']['id']
        username = content['data']['me']['username']
        self.assertEqual(id, '1')
        self.assertEqual(username, 'ali')

    def test_blog(self):
        response = self.query(
            '''
            {
              blogs {
                title
              }
            }
            ''')
        content = json.loads(response.content)
        blogs = content['data']['blogs']
        title = blogs[0]['title']

        self.assertEqual(len(blogs), 1)
        self.assertEqual(title, "ali's blog")

    def test_tags(self):
        response = self.query(
            '''
            {
              tags {
                name
              }
            }
            ''')
        content = json.loads(response.content)
        tags = content['data']['tags']

        self.assertEqual(len(tags), 4)
        self.assertContains(response, 'Django')

    def test_posts_anonymous(self):
        """ دریافت همه پست ها با کاربر ناشناس. """
        response = self.query(
            '''
            {
              posts {
                edges {
                  node {
                    title
                  }
                }
              }
            }
            ''')
        content = json.loads(response.content)
        posts_nodes = content['data']['posts']['edges']

        self.assertEqual(len(posts_nodes), 2)
        self.assertEqual(posts_nodes[0]['node']['title'],'my first post')

    def test_posts_ali(self):
        """ دریافت همه پست ها با کاربر علی. """
        token = self.take_token()
        response = self.query(
            '''
            {
              posts {
                edges {
                  node {
                    title
                  }
                }
              }
            }
            ''',
            headers=
            {
                "HTTP_AUTHORIZATION": "jwt " + token
            }
        )
        content = json.loads(response.content)
        posts_nodes = content['data']['posts']['edges']

        self.assertEqual(len(posts_nodes), 3)
        self.assertEqual(posts_nodes[0]['node']['title'],'my first post')

    def test_create_post(self):
        token = self.take_token()
        response = self.query(
            '''
            mutation {
              createPost(
                input: { blogId: 1, title: "test blog", body: "test body", isPublic: true }
              ) {
                id
              }
            }
            ''',
            headers=
            {
                "HTTP_AUTHORIZATION": "jwt " + token
            })
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        ali_profile = models.Profile.objects.get(id=1)
        ali_posts = models.Post.objects.filter(blog__owner=ali_profile)
        self.assertEqual(len(ali_posts), 4)

    def test_create_post_anonymous(self):
        response = self.query('''
        mutation {
          createPost(
            input: { blogId: 1, title: "test blog", body: "test body", isPublic: true }
          ) {
            id
          }
        }
        ''')
        content = json.loads(response.content)
        self.assertResponseHasErrors(response, "You do not have permission to perform this action")

    def test_create_post_blog_not_exist(self):
        """  تلاش برای ایجاد پست در بلاگی که وجود ندارد"""
        response = self.query('''
        mutation {
          createPost(
            input: { blogId: 100, title: "test blog", body: "test body", isPublic: true }
          ) {
            id
          }
        }
        ''')
        content = json.loads(response.content)
        self.assertResponseHasErrors(response)

    def test_tag_post(self):
        token = self.take_token()
        response = self.query('''
            mutation {
              tagPost(postId: 3, tagsId: [1, 2, 3, 4, 111]) {
                post {
                  id
                  title
                  tags {
                    name
                  }
                }
              }
            } ''',
                              headers=
                              {
                                  "HTTP_AUTHORIZATION": "jwt " + token
                              }
                              )
        content = json.loads(response.content)
        tags = content['data']['tagPost']['post']['tags']
        self.assertEqual(len(tags), 4)

    def test_delete_tag_post(self):
        token = self.take_token()
        response = self.query('''
          mutation {
              deleteTagPost(postId: 3, tagsId: [1]) {
                post {
                  id
                  title
                  tags {
                    id
                    name
                  }
                }
              }
            }
            ''',
                              headers=
                              {
                                  "HTTP_AUTHORIZATION": "jwt " + token
                              }
                              )
        content = json.loads(response.content)
        tags = content['data']['deleteTagPost']['post']['tags']
        self.assertEqual(len(tags), 1)