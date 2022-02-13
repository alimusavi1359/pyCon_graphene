from blog import models

tag_django = models.Tag.objects.create(name='Django')
tag_python = models.Tag.objects.create(name='python')
tag_pycon = models.Tag.objects.create(name='pycon')
tag_iran = models.Tag.objects.create(name='iran')

# models.User.objects.all().delete()
ali = models.User.objects.create_user(username='ali', password='ali123')
ali_profile = models.Profile.objects.create(user=ali, first_name='ali')
ali_blog = models.Blog.objects.create(title="ali's blog", owner=ali_profile, description='taking about Django')

ali_post1 = models.Post.objects.create(blog=ali_blog, title='my first post', body='my first post my first post')

ali_post2 = models.Post.objects.create(blog=ali_blog, title='first post about django', body='django is easy')
ali_post2.tags.add(tag_django)
ali_post2.save()
ali_comment_post2 = models.Comment.objects.create(post=ali_post2,user=ali_profile,body="my first comment")

ali_post3 = models.Post.objects.create(blog=ali_blog, title='django private post', body='this post not public.',
                                       is_public=False)
ali_post3.tags.add(tag_django)
ali_post3.tags.add(tag_pycon)
ali_post3.save()

print(models.Profile.objects.count())
